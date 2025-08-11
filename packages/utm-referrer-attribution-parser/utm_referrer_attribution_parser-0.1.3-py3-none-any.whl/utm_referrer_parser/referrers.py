"""
Referrer database management and parsing functionality.

Handles loading, parsing, and querying the Snowplow referrer database
for accurate source/medium classification.
"""

import os
import hashlib
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qsl
import yaml
from .updater import get_updated_referrers_data
from .cache import get_referrer_parser_cache, create_cache_key


class ReferrerParser:
    """Parser for referrer URLs using Snowplow database."""

    def __init__(self, referrers_data: Optional[Dict] = None) -> None:
        """Initialize with referrer database."""
        self._referrers_index: Dict[str, Dict[str, str]] = {}
        if referrers_data:
            self._build_index(referrers_data)

    def _build_index(self, referrers_data: Dict) -> None:
        """Build domain index from referrers data for fast lookups."""
        for medium, providers in referrers_data.items():
            for provider_name, config in providers.items():
                domains = config.get('domains', [])
                parameters = config.get('parameters', [])

                for domain in domains:
                    self._referrers_index[domain] = {
                        'name': provider_name,
                        'medium': medium,
                        'parameters': parameters
                    }

    def parse(self, referrer_url: str, current_url: Optional[str] = None) -> Dict[str, Optional[str]]:
        """
        Parse referrer URL and return attribution information.
        
        Args:
            referrer_url: The referrer URL to parse
            current_url: Optional current URL for internal referrer detection
            
        Returns:
            Dict containing referrer information:
            - source: The referrer source name (e.g., "Google")
            - medium: The referrer medium (e.g., "search", "social", "email")
            - term: Search term if available
        """
        # Check cache first
        cache = get_referrer_parser_cache()
        cache_key = create_cache_key(referrer_url, current_url or '')
        cached_result = cache.get_parse_result(cache_key)
        if cached_result is not None:
            return cached_result

        result = {
            'source': None,
            'medium': 'unknown',
            'term': None
        }

        # Handle non-string inputs gracefully
        if not referrer_url or not isinstance(referrer_url, str) or not referrer_url.strip():
            result['source'] = '(direct)'
            result['medium'] = '(none)'
            # Cache the result before returning
            cache.put_parse_result(cache_key, result)
            return result

        try:
            ref_uri = urlparse(referrer_url)
            ref_host = ref_uri.hostname

            if not ref_host or ref_uri.scheme not in {'http', 'https'}:
                return result

            # Check for internal referrer using root domain comparison
            if current_url:
                curr_uri = urlparse(current_url)
                if curr_uri.hostname:
                    ref_root = self._get_root_domain(ref_host)
                    curr_root = self._get_root_domain(curr_uri.hostname)
                    if ref_root and curr_root and ref_root == curr_root:
                        result['source'] = '(internal)'
                        result['medium'] = 'internal'
                        # Cache the result before returning
                        cache.put_parse_result(cache_key, result)
                        return result

            # Look up referrer in database
            referrer_info = self._lookup_referrer(ref_host, ref_uri.path)
            if not referrer_info:
                # Unknown referrer - classify as referral traffic
                result['source'] = ref_host
                result['medium'] = 'referral'
                # Cache the result before returning
                cache.put_parse_result(cache_key, result)
                return result

            result['source'] = referrer_info['name'].lower()
            result['medium'] = 'organic' if referrer_info['medium'] == 'search' else referrer_info['medium']

            # Extract search term for search engines (check original medium before mapping)
            if referrer_info['medium'] == 'search' and referrer_info['parameters']:
                search_term = self._extract_search_term(ref_uri.query, referrer_info['parameters'])
                if search_term:
                    result['term'] = search_term

            # Cache the result before returning
            cache.put_parse_result(cache_key, result)
            return result

        except Exception:
            # Cache the result even on exception
            cache.put_parse_result(cache_key, result)
            return result

    def _lookup_referrer(self, hostname: str, path: str = '') -> Optional[Dict]:
        """Look up referrer info by hostname with fallback logic."""
        # Try exact hostname match first
        if hostname in self._referrers_index:
            return self._referrers_index[hostname]

        # Try hostname + path combinations
        if path:
            path_variants = [hostname + path]
            path_parts = path.split('/')
            if len(path_parts) > 1:
                path_variants.append(hostname + '/' + path_parts[1])

            for variant in path_variants:
                if variant in self._referrers_index:
                    return self._referrers_index[variant]

        # Try intelligent subdomain fallback using tldextract
        if '.' in hostname:
            try:
                # Use tldextract for more intelligent domain parsing
                import tldextract
                extracted = tldextract.extract(hostname.lower())
                
                if extracted.domain and extracted.suffix:
                    # Try root domain (e.g., google.co.uk)
                    root_domain = f"{extracted.domain}.{extracted.suffix}"
                    if root_domain != hostname:
                        result = self._lookup_referrer(root_domain, path)
                        if result:
                            return result
                
                # Fallback to old recursive logic if tldextract fails
                idx = hostname.index('.')
                parent_domain = hostname[idx + 1:]
                return self._lookup_referrer(parent_domain, path)
                
            except (ImportError, ValueError):
                # Fallback to old recursive logic
                try:
                    idx = hostname.index('.')
                    parent_domain = hostname[idx + 1:]
                    return self._lookup_referrer(parent_domain, path)
                except ValueError:
                    pass

        return None

    def _get_root_domain(self, hostname: str) -> Optional[str]:
        """
        Extract root domain from hostname for internal referrer detection.
        
        Uses tldextract to properly handle all TLDs including complex cases
        like .co.uk, .com.au, etc.
        
        Examples:
            - acme-corp.de -> acme-corp.de
            - shop.acme-corp.de -> acme-corp.de  
            - www.example.com -> example.com
            - subdomain.test.example.co.uk -> example.co.uk
        """
        if not hostname:
            return None
            
        try:
            import tldextract
            
            # Extract domain parts using tldextract
            extracted = tldextract.extract(hostname.lower())
            
            # Return domain + suffix (e.g., "example" + "co.uk" = "example.co.uk")
            if extracted.domain and extracted.suffix:
                return f"{extracted.domain}.{extracted.suffix}"
            elif extracted.domain:
                # Fallback for cases where suffix detection fails
                return extracted.domain
            else:
                return None
                
        except ImportError:
            # Fallback to simple logic if tldextract is not available
            # This should not happen since tldextract is now a dependency
            parts = hostname.lower().split('.')
            return '.'.join(parts[-2:]) if len(parts) >= 2 else hostname

    def _extract_search_term(self, query_string: str, parameters: List[str]) -> Optional[str]:
        """Extract search term from query string using known parameters."""
        if not query_string or not parameters:
            return None

        try:
            for param, value in parse_qsl(query_string):
                if param.lower() in [p.lower() for p in parameters]:
                    return value.strip() if value else None
        except Exception:
            pass

        return None


def load_referrers_yaml(file_path: str) -> Dict:
    """Load referrers database from YAML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def load_bundled_referrers() -> Dict:
    """Load bundled referrers database."""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    yaml_path = os.path.join(data_dir, 'referers.yaml')

    # Try to load bundled YAML file
    if os.path.exists(yaml_path):
        return load_referrers_yaml(yaml_path)

    return {}


def create_referrer_parser(force_update: bool = False) -> ReferrerParser:
    """
    Create ReferrerParser instance with auto-updated data.
    
    Args:
        force_update: Force download of latest database
        
    Returns:
        ReferrerParser instance with latest or cached data
    """
    # Get updated referrers data
    referrers_data = get_updated_referrers_data(force_update)

    # Create hash of data for caching
    data_str = str(sorted(referrers_data.items()))
    data_hash = hashlib.md5(data_str.encode()).hexdigest()

    # Check if we have a cached parser for this data
    cache = get_referrer_parser_cache()
    cached_parser = cache.get_parser(data_hash)
    if cached_parser is not None:
        return cached_parser

    # Create new parser and cache it
    parser = ReferrerParser(referrers_data)
    cache.put_parser(data_hash, parser)

    return parser


