"""Tests for main attribution parsing functionality."""

import pytest
from utm_referrer_parser import parse_attribution


class TestParseAttribution:
    """Tests for parse_attribution function."""
    
    def test_google_ads_click(self):
        """Test Google Ads click attribution."""
        tracking_data = {
            "dl": "https://mysite.com/landing?utm_source=google&utm_medium=cpc&utm_campaign=winter_sale&gclid=CjwKCAiA",
            "dr": "https://www.google.com/aclk?sa=L&ai=...",
            "bu": "https://mysite.com",
        }
        
        result = parse_attribution(tracking_data)
        
        assert result['utm_source'] == 'google'
        assert result['utm_medium'] == 'cpc'
        assert result['utm_campaign'] == 'winter_sale'
        assert result['gclid'] == 'CjwKCAiA'
        assert result['attribution_source'] == 'google'
        assert result['attribution_medium'] == 'cpc'
    
    def test_facebook_ad_click(self):
        """Test Facebook ad click attribution."""
        tracking_data = {
            "dl": "https://mysite.com/product?fbclid=IwAR1234567890",
            "dr": "https://www.facebook.com/",
            "bu": "https://mysite.com",
        }
        
        result = parse_attribution(tracking_data)
        
        assert result['fbclid'] == 'IwAR1234567890'
        assert result['attribution_source'] == 'facebook'
        assert result['attribution_medium'] == 'cpc'
    
    def test_organic_google_search(self):
        """Test organic Google search attribution."""
        tracking_data = {
            "dl": "https://mysite.com/blog/analytics-guide",
            "dr": "https://www.google.com/search?q=web+analytics+guide",
            "bu": "https://mysite.com",
        }
        
        result = parse_attribution(tracking_data)
        
        # Should get referrer information
        assert result['referrer_source'] == 'google'
        assert result['referrer_medium'] == 'organic'
        assert result.get('referrer_term') == 'web analytics guide'
        assert result['attribution_source'] == 'google'
        assert result['attribution_medium'] == 'organic'
    
    def test_direct_traffic(self):
        """Test direct traffic attribution."""
        tracking_data = {
            "dl": "https://mysite.com/",
            "dr": "",  # Empty referrer
            "bu": "https://mysite.com",
        }
        
        result = parse_attribution(tracking_data)
        
        assert result['referrer_source'] == '(direct)'
        assert result['referrer_medium'] == '(none)'
        assert result['attribution_source'] == '(direct)'
        assert result['attribution_medium'] == '(none)'
    
    def test_utm_override_referrer(self):
        """Test that UTM parameters override referrer analysis."""
        tracking_data = {
            "dl": "https://mysite.com/?utm_source=newsletter&utm_medium=email&utm_campaign=march2024",
            "dr": "https://www.google.com/search?q=test",
            "bu": "https://mysite.com",
        }
        
        result = parse_attribution(tracking_data)
        
        # UTM should take priority
        assert result['attribution_source'] == 'newsletter'
        assert result['attribution_medium'] == 'email'
        assert result['utm_campaign'] == 'march2024'
        
        # But referrer info should still be available
        assert result['referrer_source'] == 'google'
        assert result['referrer_medium'] == 'organic'
    
    def test_multiple_click_ids(self):
        """Test handling of multiple click IDs."""
        tracking_data = {
            "dl": "https://mysite.com/?gclid=abc123&fbclid=def456",
            "dr": "",
            "bu": "https://mysite.com",
        }
        
        result = parse_attribution(tracking_data)
        
        # Should extract both
        assert result['gclid'] == 'abc123'
        assert result['fbclid'] == 'def456'
        
        # Google should take priority in attribution logic
        assert result['attribution_source'] == 'google'
        assert result['attribution_medium'] == 'cpc'
    
    def test_preserve_original_data(self):
        """Test that original tracking data is preserved."""
        tracking_data = {
            "dl": "https://mysite.com/?utm_source=test",
            "dr": "https://example.com",
            "bu": "https://mysite.com",
            "aid": "tracking_id_123",
            "ua": "Mozilla/5.0...",
            "ip_address": "192.168.1.1",
        }
        
        result = parse_attribution(tracking_data)
        
        # Original data should be preserved
        assert result['aid'] == 'tracking_id_123'
        assert result['ua'] == 'Mozilla/5.0...'
        assert result['ip_address'] == '192.168.1.1'
        
        # Plus attribution data should be added
        assert result['utm_source'] == 'test'
        assert 'attribution_source' in result
    
    def test_empty_tracking_data(self):
        """Test handling of empty tracking data."""
        result = parse_attribution({})
        
        assert result['attribution_source'] == '(direct)'
        assert result['attribution_medium'] == '(none)'
    
    def test_malformed_urls(self):
        """Test handling of malformed URLs."""
        tracking_data = {
            "dl": "not-a-url",
            "dr": "also-not-a-url",
            "bu": "https://mysite.com",
        }
        
        result = parse_attribution(tracking_data)
        
        # Should handle gracefully
        assert result['attribution_source'] == '(direct)'
        assert result['attribution_medium'] == '(none)'