"""
Weekly database auto-update mechanism for Snowplow referrer database.

Handles downloading, caching, and updating the referrer database with
graceful fallbacks and error handling.
"""

import time
import json
from typing import Dict, Optional
from pathlib import Path
import requests
import yaml


SNOWPLOW_YAML_URL = "https://s3-eu-west-1.amazonaws.com/snowplow-hosted-assets/third-party/referer-parser/referers-latest.yaml"
SNOWPLOW_JSON_URL = "https://s3-eu-west-1.amazonaws.com/snowplow-hosted-assets/third-party/referer-parser/referers-latest.json"

# Cache for 7 days (weekly updates)
CACHE_DURATION_SECONDS = 7 * 24 * 60 * 60  # 7 days


class DatabaseUpdater:
    """Handles downloading and caching of Snowplow referrer database."""

    def __init__(self, cache_dir: Optional[str] = None) -> None:
        """
        Initialize database updater.
        
        Args:
            cache_dir: Directory to store cached database files.
                      Defaults to package data directory.
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Use package data directory
            package_dir = Path(__file__).parent
            self.cache_dir = package_dir / 'data'

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.yaml_cache_path = self.cache_dir / 'referers.yaml'
        self.json_cache_path = self.cache_dir / 'referers.json'
        self.metadata_path = self.cache_dir / 'cache_metadata.json'

    def get_referrers_data(self, force_update: bool = False) -> Dict:
        """
        Get referrers database, updating if necessary.
        
        Args:
            force_update: Force download even if cache is valid
            
        Returns:
            Dictionary containing referrers database
        """
        # Check if update is needed
        if not force_update and self._is_cache_valid():
            return self._load_cached_data()

        # Try to update from remote
        success = self._update_from_remote()
        if success:
            return self._load_cached_data()

        # Fall back to existing cache or bundled data
        return self._load_fallback_data()

    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid (not expired)."""
        if not self.yaml_cache_path.exists() and not self.json_cache_path.exists():
            return False

        if not self.metadata_path.exists():
            return False

        try:
            with open(self.metadata_path, 'r') as f:
                metadata = json.load(f)

            last_update = metadata.get('last_update', 0)
            return (time.time() - last_update) < CACHE_DURATION_SECONDS

        except Exception:
            return False

    def _update_from_remote(self) -> bool:
        """
        Download latest referrers database from Snowplow.
        
        Returns:
            True if update was successful, False otherwise
        """
        # Try YAML first (preferred format)
        if self._download_file(SNOWPLOW_YAML_URL, self.yaml_cache_path):
            self._update_metadata()
            return True

        # Fall back to JSON
        if self._download_file(SNOWPLOW_JSON_URL, self.json_cache_path):
            self._update_metadata()
            return True

        return False

    def _download_file(self, url: str, destination: Path) -> bool:
        """
        Download file from URL to destination.
        
        Args:
            url: URL to download from
            destination: Local file path to save to
            
        Returns:
            True if download was successful, False otherwise
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Write to temporary file first, then move to avoid corruption
            temp_path = destination.with_suffix(destination.suffix + '.tmp')
            with open(temp_path, 'wb') as f:
                f.write(response.content)

            # Move temp file to final location
            temp_path.replace(destination)
            return True

        except Exception:
            # Clean up temp file if it exists
            temp_path = destination.with_suffix(destination.suffix + '.tmp')
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            return False

    def _update_metadata(self) -> None:
        """Update cache metadata with current timestamp."""
        try:
            metadata = {
                'last_update': time.time(),
                'version': '1.0'
            }
            with open(self.metadata_path, 'w') as f:
                json.dump(metadata, f)
        except Exception:
            pass

    def _load_cached_data(self) -> Dict:
        """Load data from cache (YAML preferred, JSON fallback)."""
        # Try YAML first
        if self.yaml_cache_path.exists():
            try:
                with open(self.yaml_cache_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                pass

        # Fall back to JSON
        if self.json_cache_path.exists():
            try:
                with open(self.json_cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f) or {}
            except Exception:
                pass

        return {}

    def _load_fallback_data(self) -> Dict:
        """Load fallback data from existing cache or return empty dict."""
        # Try to load any existing cached data, even if expired
        cached_data = self._load_cached_data()
        if cached_data:
            return cached_data

        # Return empty dict if no data available
        return {}

    def force_update(self) -> bool:
        """Force update of referrers database."""
        return self._update_from_remote()

    def clear_cache(self) -> None:
        """Clear all cached data."""
        files_to_remove = [
            self.yaml_cache_path,
            self.json_cache_path,
            self.metadata_path
        ]

        for file_path in files_to_remove:
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception:
                    pass


# Global updater instance
_global_updater: Optional[DatabaseUpdater] = None


def get_database_updater() -> DatabaseUpdater:
    """Get global database updater instance."""
    global _global_updater
    if _global_updater is None:
        _global_updater = DatabaseUpdater()
    return _global_updater


def get_updated_referrers_data(force_update: bool = False) -> Dict:
    """
    Get referrers database with automatic updates.
    
    Args:
        force_update: Force download even if cache is valid
        
    Returns:
        Dictionary containing referrers database
    """
    updater = get_database_updater()
    return updater.get_referrers_data(force_update)
