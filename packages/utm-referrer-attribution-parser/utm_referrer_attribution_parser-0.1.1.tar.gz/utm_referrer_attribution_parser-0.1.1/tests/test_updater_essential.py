"""Essential tests for database updater functionality.

Focuses on core functionality that matters for production use.
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests
import yaml

from utm_referrer_parser.updater import (
    CACHE_DURATION_SECONDS,
    DatabaseUpdater,
    get_database_updater,
    get_updated_referrers_data,
)


class TestDatabaseUpdaterCore:
    """Core functionality tests for DatabaseUpdater."""

    def setup_method(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.updater = DatabaseUpdater(cache_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test that updater initializes correctly."""
        assert self.updater.cache_dir.exists()
        assert self.updater.cache_dir.is_dir()

    def test_cache_validation_logic(self):
        """Test cache validation with recent vs expired data."""
        # Test with recent data (valid)
        metadata = {
            'last_update': time.time() - 3600,  # 1 hour ago
            'version': '1.0'
        }
        with open(self.updater.metadata_path, 'w') as f:
            json.dump(metadata, f)
        self.updater.yaml_cache_path.touch()
        
        assert self.updater._is_cache_valid() is True
        
        # Test with expired data (invalid)
        metadata['last_update'] = time.time() - (CACHE_DURATION_SECONDS + 3600)
        with open(self.updater.metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        assert self.updater._is_cache_valid() is False

    def test_cache_invalid_scenarios(self):
        """Test various cache invalidation scenarios."""
        # No files exist
        assert self.updater._is_cache_valid() is False
        
        # File exists but no metadata
        self.updater.yaml_cache_path.touch()
        assert self.updater._is_cache_valid() is False
        
        # Corrupted metadata
        with open(self.updater.metadata_path, 'w') as f:
            f.write("invalid json")
        assert self.updater._is_cache_valid() is False

    @patch('utm_referrer_parser.updater.requests.get')
    def test_successful_download(self, mock_get):
        """Test successful file download."""
        mock_response = Mock()
        mock_response.content = b"test: data"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        test_path = Path(self.temp_dir) / "test.yaml"
        result = self.updater._download_file("http://example.com/test.yaml", test_path)
        
        assert result is True
        assert test_path.exists()
        assert test_path.read_bytes() == b"test: data"

    @patch('utm_referrer_parser.updater.requests.get')
    def test_download_network_failure(self, mock_get):
        """Test download failure handling."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        test_path = Path(self.temp_dir) / "test.yaml"
        result = self.updater._download_file("http://example.com/test.yaml", test_path)
        
        assert result is False
        assert not test_path.exists()

    def test_data_loading_priority(self):
        """Test that YAML takes priority over JSON."""
        yaml_data = {'search': {'Google': {'domains': ['google.com']}}}
        json_data = {'search': {'Bing': {'domains': ['bing.com']}}}
        
        # Create both files
        with open(self.updater.yaml_cache_path, 'w') as f:
            yaml.dump(yaml_data, f)
        with open(self.updater.json_cache_path, 'w') as f:
            json.dump(json_data, f)
        
        result = self.updater._load_cached_data()
        assert result == yaml_data  # YAML should win

    def test_json_fallback(self):
        """Test JSON fallback when YAML is unavailable."""
        json_data = {'search': {'Bing': {'domains': ['bing.com']}}}
        
        with open(self.updater.json_cache_path, 'w') as f:
            json.dump(json_data, f)
        
        result = self.updater._load_cached_data()
        assert result == json_data

    def test_corrupted_yaml_fallback(self):
        """Test fallback to JSON when YAML is corrupted."""
        json_data = {'search': {'Bing': {'domains': ['bing.com']}}}
        
        # Corrupted YAML
        with open(self.updater.yaml_cache_path, 'w') as f:
            f.write("invalid: yaml: [")
        
        # Valid JSON
        with open(self.updater.json_cache_path, 'w') as f:
            json.dump(json_data, f)
        
        result = self.updater._load_cached_data()
        assert result == json_data

    @patch.object(DatabaseUpdater, '_update_from_remote')
    @patch.object(DatabaseUpdater, '_is_cache_valid')  
    @patch.object(DatabaseUpdater, '_load_cached_data')
    def test_get_data_with_valid_cache(self, mock_load, mock_valid, mock_update):
        """Test getting data when cache is valid."""
        cached_data = {'search': {'Google': {'domains': ['google.com']}}}
        
        mock_valid.return_value = True
        mock_load.return_value = cached_data
        
        result = self.updater.get_referrers_data()
        
        assert result == cached_data
        mock_update.assert_not_called()  # Should not attempt update

    @patch.object(DatabaseUpdater, '_update_from_remote')
    @patch.object(DatabaseUpdater, '_is_cache_valid')
    @patch.object(DatabaseUpdater, '_load_fallback_data')
    def test_get_data_with_failed_update(self, mock_fallback, mock_valid, mock_update):
        """Test getting data when update fails."""
        fallback_data = {'search': {'Old': {'domains': ['old.com']}}}
        
        mock_valid.return_value = False
        mock_update.return_value = False  # Update failed
        mock_fallback.return_value = fallback_data
        
        result = self.updater.get_referrers_data()
        
        assert result == fallback_data
        mock_update.assert_called_once()
        mock_fallback.assert_called_once()

    def test_force_update_bypasses_cache(self):
        """Test that force update ignores valid cache."""
        # Create valid cache
        metadata = {'last_update': time.time() - 3600, 'version': '1.0'}
        with open(self.updater.metadata_path, 'w') as f:
            json.dump(metadata, f)
        self.updater.yaml_cache_path.touch()
        
        with patch.object(self.updater, '_update_from_remote') as mock_update:
            mock_update.return_value = False
            
            # Should attempt update despite valid cache
            self.updater.get_referrers_data(force_update=True)
            mock_update.assert_called_once()

    def test_clear_cache_functionality(self):
        """Test cache clearing removes all files."""
        # Create cache files
        self.updater.yaml_cache_path.touch()
        self.updater.json_cache_path.touch()
        self.updater.metadata_path.touch()
        
        self.updater.clear_cache()
        
        assert not self.updater.yaml_cache_path.exists()
        assert not self.updater.json_cache_path.exists()
        assert not self.updater.metadata_path.exists()


class TestGlobalUpdaterFunctions:
    """Test global utility functions."""

    def test_singleton_updater(self):
        """Test that global updater returns same instance."""
        updater1 = get_database_updater()
        updater2 = get_database_updater()
        assert updater1 is updater2

    @patch('utm_referrer_parser.updater.get_database_updater')
    def test_get_updated_data_wrapper(self, mock_get_updater):
        """Test the convenience wrapper function."""
        mock_updater = Mock()
        mock_data = {'search': {'Google': {'domains': ['google.com']}}}
        mock_updater.get_referrers_data.return_value = mock_data
        mock_get_updater.return_value = mock_updater
        
        result = get_updated_referrers_data()
        assert result == mock_data
        mock_updater.get_referrers_data.assert_called_once_with(False)
        
        # Test with force update
        get_updated_referrers_data(force_update=True)
        mock_updater.get_referrers_data.assert_called_with(True)


class TestUpdateIntegration:
    """Integration tests for update functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('utm_referrer_parser.updater.requests.get')
    def test_complete_update_cycle(self, mock_get):
        """Test complete update from download to data access."""
        updater = DatabaseUpdater(cache_dir=self.temp_dir)
        
        # Mock successful download
        test_data = {
            'search': {
                'Google': {
                    'domains': ['google.com', 'google.co.uk'],
                    'parameters': ['q', 'query']
                }
            }
        }
        
        mock_response = Mock()
        mock_response.content = yaml.dump(test_data).encode()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = updater.get_referrers_data(force_update=True)
        
        assert result == test_data
        assert updater.yaml_cache_path.exists()
        assert updater.metadata_path.exists()

    def test_fallback_to_existing_on_network_error(self):
        """Test graceful fallback when network is unavailable."""
        updater = DatabaseUpdater(cache_dir=self.temp_dir)
        
        # Create existing cache
        existing_data = {'search': {'Google': {'domains': ['google.com']}}}
        with open(updater.yaml_cache_path, 'w') as f:
            yaml.dump(existing_data, f)
        
        with patch('utm_referrer_parser.updater.requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Network unavailable")
            
            # Should return existing data despite network failure
            result = updater.get_referrers_data(force_update=True)
            assert result == existing_data

    def test_error_handling_doesnt_crash(self):
        """Test that various error conditions don't crash the system."""
        updater = DatabaseUpdater(cache_dir=self.temp_dir)
        
        # Should handle gracefully and return empty dict
        result = updater.get_referrers_data()
        assert isinstance(result, dict)
        
        # Should handle metadata update errors gracefully
        updater._update_metadata()  # Should not raise
        
        # Should handle clear cache on non-existent files
        updater.clear_cache()  # Should not raise