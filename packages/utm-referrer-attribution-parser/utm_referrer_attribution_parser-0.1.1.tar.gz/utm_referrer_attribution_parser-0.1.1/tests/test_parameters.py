"""Tests for parameter extraction functionality."""

import pytest
from utm_referrer_parser.parameters import ParameterExtractor, create_parameter_extractor


class TestParameterExtractor:
    """Tests for ParameterExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = create_parameter_extractor()
    
    def test_utm_parameters(self):
        """Test extraction of standard UTM parameters."""
        url = "https://example.com/?utm_source=google&utm_medium=cpc&utm_campaign=test&utm_term=keyword&utm_content=ad1&utm_id=123"
        
        result = self.extractor.extract_from_url(url)
        
        assert result['utm_source'] == 'google'
        assert result['utm_medium'] == 'cpc'
        assert result['utm_campaign'] == 'test'
        assert result['utm_term'] == 'keyword'
        assert result['utm_content'] == 'ad1'
        assert result['utm_id'] == '123'
    
    def test_google_ads_parameters(self):
        """Test extraction of Google Ads parameters."""
        url = "https://example.com/?gclid=abc123&gbraid=def456&wbraid=ghi789&gad_source=1&srsltid=xyz"
        
        result = self.extractor.extract_from_url(url)
        
        assert result['gclid'] == 'abc123'
        assert result['gbraid'] == 'def456'
        assert result['wbraid'] == 'ghi789'
        assert result['gad_source'] == '1'
        assert result['srsltid'] == 'xyz'
    
    def test_social_media_parameters(self):
        """Test extraction of social media parameters."""
        url = "https://example.com/?fbclid=fb123&ttclid=tt456&twclid=tw789&li_fat_id=li123"
        
        result = self.extractor.extract_from_url(url)
        
        assert result['fbclid'] == 'fb123'
        assert result['ttclid'] == 'tt456'
        assert result['twclid'] == 'tw789'
        assert result['li_fat_id'] == 'li123'
    
    def test_email_marketing_parameters(self):
        """Test extraction of email marketing parameters."""
        url = "https://example.com/?mc_cid=mailchimp123&mc_eid=email456&ml_subscriber_hash=hash789"
        
        result = self.extractor.extract_from_url(url)
        
        assert result['mc_cid'] == 'mailchimp123'
        assert result['mc_eid'] == 'email456'
        assert result['ml_subscriber_hash'] == 'hash789'
    
    def test_mixed_case_parameters(self):
        """Test handling of mixed case parameters."""
        url = "https://example.com/?UTM_SOURCE=Google&Utm_Medium=CPC&FBCLID=Facebook123"
        
        result = self.extractor.extract_from_url(url)
        
        # UTM parameters now preserve case for values
        assert result['utm_source'] == 'Google'
        assert result['utm_medium'] == 'CPC'
        
        # Click IDs should preserve case
        assert result['fbclid'] == 'Facebook123'
    
    def test_empty_parameter_values(self):
        """Test handling of empty parameter values."""
        url = "https://example.com/?utm_source=&utm_medium=cpc&gclid="
        
        result = self.extractor.extract_from_url(url)
        
        assert result['utm_source'] == ''
        assert result['utm_medium'] == 'cpc'
        assert result['gclid'] == ''
    
    def test_no_query_string(self):
        """Test URL with no query string."""
        url = "https://example.com/page"
        
        result = self.extractor.extract_from_url(url)
        
        assert result == {}
    
    def test_ignore_non_tracking_parameters(self):
        """Test that non-tracking parameters are ignored."""
        url = "https://example.com/?utm_source=test&page=1&sort=date&other=value"
        
        result = self.extractor.extract_from_url(url)
        
        assert result == {'utm_source': 'test'}
        assert 'page' not in result
        assert 'sort' not in result
        assert 'other' not in result
    
    def test_custom_parameters(self):
        """Test custom parameter extraction."""
        custom_params = {'custom_id', 'my_param'}
        extractor = ParameterExtractor(custom_params)
        
        url = "https://example.com/?utm_source=test&custom_id=123&my_param=value&ignored=nope"
        
        result = extractor.extract_from_url(url)
        
        assert result['utm_source'] == 'test' 
        assert result['custom_id'] == '123'
        assert result['my_param'] == 'value'
        assert 'ignored' not in result
    
    def test_extract_from_tracking_data(self):
        """Test parameter extraction from tracking data dict."""
        tracking_data = {
            "dl": "https://example.com/?utm_source=google&gclid=abc123",
            "dr": "https://social.com/?fbclid=fb456",
            "bu": "https://example.com"
        }
        
        result = self.extractor.extract_from_tracking_data(tracking_data)
        
        # Should get parameters from both URLs
        assert result['utm_source'] == 'google'
        assert result['gclid'] == 'abc123'
        assert result['fbclid'] == 'fb456'
    
    def test_parameter_priority_in_tracking_data(self):
        """Test that dl parameters take priority over dr parameters."""
        tracking_data = {
            "dl": "https://example.com/?utm_source=newsletter",
            "dr": "https://social.com/?utm_source=facebook",
        }
        
        result = self.extractor.extract_from_tracking_data(tracking_data)
        
        # dl should take priority
        assert result['utm_source'] == 'newsletter'
    
    def test_get_parameter_categories(self):
        """Test parameter categorization."""
        params = {
            'utm_source': 'google',
            'utm_medium': 'cpc',
            'gclid': 'abc123',
            'fbclid': 'fb456',
            'mc_cid': 'mail123',
            'pk_campaign': 'piwik123'
        }
        
        categories = self.extractor.get_parameter_categories(params)
        
        assert 'utm_source' in categories['utm']
        assert 'utm_medium' in categories['utm']
        assert 'gclid' in categories['google_ads']
        assert 'fbclid' in categories['social_media']
        assert 'mc_cid' in categories['email_marketing']
        assert 'pk_campaign' in categories['analytics']
    
    def test_malformed_url(self):
        """Test handling of malformed URLs."""
        malformed_url = "not-a-valid-url"
        
        result = self.extractor.extract_from_url(malformed_url)
        
        assert result == {}
    
    def test_empty_url(self):
        """Test handling of empty URL."""
        result = self.extractor.extract_from_url("")
        assert result == {}
        
        result = self.extractor.extract_from_url(None)
        assert result == {}