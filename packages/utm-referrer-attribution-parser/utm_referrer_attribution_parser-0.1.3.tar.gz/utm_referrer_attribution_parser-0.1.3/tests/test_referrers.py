"""Tests for referrer parsing functionality."""

import pytest
from utm_referrer_parser.referrers import ReferrerParser


class TestReferrerParser:
    """Tests for ReferrerParser class."""
    
    def setup_method(self):
        """Set up test fixtures with sample referrer data."""
        self.sample_data = {
            'search': {
                'Google': {
                    'domains': ['www.google.com', 'google.com', 'google.co.uk'],
                    'parameters': ['q', 'query']
                },
                'Bing': {
                    'domains': ['www.bing.com', 'bing.com'],
                    'parameters': ['q']
                }
            },
            'social': {
                'Facebook': {
                    'domains': ['www.facebook.com', 'facebook.com', 'm.facebook.com']
                },
                'Twitter': {
                    'domains': ['twitter.com', 'x.com', 't.co']
                }
            },
            'email': {
                'Gmail': {
                    'domains': ['mail.google.com']
                }
            },
            'unknown': {
                'Google Services': {
                    'domains': ['drive.google.com', 'docs.google.com']
                }
            }
        }
        self.parser = ReferrerParser(self.sample_data)
    
    def test_google_search_with_term(self):
        """Test parsing Google search with search term."""
        referrer_url = "https://www.google.com/search?q=web+analytics+guide&source=hp"
        
        result = self.parser.parse(referrer_url)
        
        assert result['source'] == 'google'
        assert result['medium'] == 'organic'
        assert result['term'] == 'web analytics guide'
    
    def test_google_search_no_term(self):
        """Test parsing Google search without search term."""
        referrer_url = "https://www.google.com/search"
        
        result = self.parser.parse(referrer_url)
        
        assert result['source'] == 'google'
        assert result['medium'] == 'organic'
        assert result['term'] is None
    
    def test_facebook_social(self):
        """Test parsing Facebook referrer."""
        referrer_url = "https://www.facebook.com/"
        
        result = self.parser.parse(referrer_url)
        
        assert result['source'] == 'facebook'
        assert result['medium'] == 'social'
        assert result['term'] is None
    
    def test_bing_search_with_term(self):
        """Test parsing Bing search with term."""
        referrer_url = "https://www.bing.com/search?q=python+tutorial"
        
        result = self.parser.parse(referrer_url)
        
        assert result['source'] == 'bing'
        assert result['medium'] == 'organic'
        assert result['term'] == 'python tutorial'
    
    def test_subdomain_matching(self):
        """Test subdomain matching falls back to parent domain."""
        referrer_url = "https://m.facebook.com/story.php"
        
        result = self.parser.parse(referrer_url)
        
        assert result['source'] == 'facebook'
        assert result['medium'] == 'social'
    
    def test_unknown_medium(self):
        """Test referrer with unknown medium."""
        referrer_url = "https://drive.google.com/file/d/123"
        
        result = self.parser.parse(referrer_url)
        
        assert result['source'] == 'google services'
        assert result['medium'] == 'unknown'
    
    def test_internal_referrer(self):
        """Test internal referrer detection."""
        referrer_url = "https://mysite.com/page1"
        current_url = "https://mysite.com/page2"
        
        result = self.parser.parse(referrer_url, current_url)
        
        assert result['source'] == '(internal)'
        assert result['medium'] == 'internal'
    
    def test_direct_traffic_empty_referrer(self):
        """Test direct traffic with empty referrer."""
        result = self.parser.parse("")
        
        assert result['source'] == '(direct)'
        assert result['medium'] == '(none)'
    
    def test_direct_traffic_none_referrer(self):
        """Test direct traffic with None referrer."""
        result = self.parser.parse(None)
        
        assert result['source'] == '(direct)'
        assert result['medium'] == '(none)'
    
    def test_unknown_referrer(self):
        """Test unknown referrer domain."""
        referrer_url = "https://unknown-site.com/page"
        
        result = self.parser.parse(referrer_url)
        
        assert result['source'] == 'unknown-site.com'
        assert result['medium'] == 'referral'
    
    def test_malformed_referrer_url(self):
        """Test malformed referrer URL."""
        referrer_url = "not-a-valid-url"
        
        result = self.parser.parse(referrer_url)
        
        assert result['source'] is None
        assert result['medium'] == 'unknown'
    
    def test_non_http_scheme(self):
        """Test non-HTTP scheme referrer."""
        referrer_url = "ftp://files.example.com/file.zip"
        
        result = self.parser.parse(referrer_url)
        
        assert result['source'] is None
        assert result['medium'] == 'unknown'
    
    def test_search_term_extraction_multiple_params(self):
        """Test search term extraction with multiple parameters."""
        # Google uses 'q', but if 'query' was also present, should still work
        referrer_url = "https://www.google.com/search?other=value&q=test+search&more=stuff"
        
        result = self.parser.parse(referrer_url)
        
        assert result['term'] == 'test search'
    
    def test_case_insensitive_parameter_matching(self):
        """Test case-insensitive parameter matching."""
        referrer_url = "https://www.google.com/search?Q=Case+Test"
        
        result = self.parser.parse(referrer_url)
        
        assert result['term'] == 'Case Test'
    
    def test_empty_search_term(self):
        """Test empty search term parameter."""
        referrer_url = "https://www.google.com/search?q="
        
        result = self.parser.parse(referrer_url)
        
        assert result['source'] == 'google'
        assert result['medium'] == 'organic'
        assert result['term'] is None
    
    def test_domain_path_matching(self):
        """Test domain + path matching logic."""
        # Test that path-specific matching works if configured
        parser_data = {
            'search': {
                'Google Images': {
                    'domains': ['www.google.com/images'],
                    'parameters': ['q']
                }
            }
        }
        parser = ReferrerParser(parser_data)
        
        referrer_url = "https://www.google.com/images/search?q=cats"
        result = parser.parse(referrer_url)
        
        # Should match the more specific path-based entry
        assert result['source'] == 'google images'
        assert result['medium'] == 'organic'