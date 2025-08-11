"""Tests for the main webmetic_referrer() function."""

import pytest
from utm_referrer_parser import webmetic_referrer, referrer


class TestWebmeticReferrer:
    """Tests for webmetic_referrer function."""
    
    def test_google_ads_complete(self):
        """Test Google Ads with full UTM parameters."""
        result = webmetic_referrer(
            url="https://site.com/?utm_source=google&utm_medium=cpc&utm_campaign=winter&utm_term=shoes&utm_content=ad1&gclid=abc123",
            referrer="https://www.google.com/aclk"
        )
        
        assert result['source'] == 'google'
        assert result['medium'] == 'cpc'
        assert result['campaign'] == 'winter'
        assert result['term'] == 'shoes'
        assert result['content'] == 'ad1'
        assert result['click_id'] == 'abc123'
        assert result['click_id_type'] == 'gclid'
        assert result['utm_source'] == 'google'
        assert result['utm_medium'] == 'cpc'
    
    def test_facebook_ad_simple(self):
        """Test simple Facebook ad click."""
        result = webmetic_referrer(
            url="https://site.com/?fbclid=IwAR123456",
            referrer="https://www.facebook.com/"
        )
        
        assert result['source'] == 'facebook'
        assert result['medium'] == 'cpc'
        assert result['click_id'] == 'IwAR123456'
        assert result['click_id_type'] == 'fbclid'
        # Should not have UTM parameters
        assert 'utm_source' not in result
        assert 'campaign' not in result or result['campaign'] is None
    
    def test_organic_search_with_term(self):
        """Test organic search with search term extraction."""
        result = webmetic_referrer(
            url="https://site.com/blog/analytics",
            referrer="https://www.google.com/search?q=web+analytics+guide"
        )
        
        assert result['source'] == 'google'
        assert result['medium'] == 'organic'
        assert result['term'] == 'web analytics guide'
    
    def test_direct_traffic(self):
        """Test direct traffic (no referrer)."""
        result = webmetic_referrer("https://site.com/")
        
        assert result['source'] == '(direct)'
        assert result['medium'] == '(none)'
        assert 'term' not in result or result['term'] is None
    
    def test_direct_traffic_empty_referrer(self):
        """Test direct traffic with empty referrer string."""
        result = webmetic_referrer("https://site.com/", referrer="")
        
        assert result['source'] == '(direct)'
        assert result['medium'] == '(none)'
    
    def test_multiple_click_ids(self):
        """Test URL with multiple click IDs."""
        result = webmetic_referrer(
            url="https://site.com/?gclid=google123&fbclid=fb456&ttclid=tiktok789"
        )
        
        # Should use first click ID found (Google has priority)
        assert result['click_id'] == 'google123'
        assert result['click_id_type'] == 'gclid'
        
        # Google should take priority in attribution
        assert result['source'] == 'google'
        assert result['medium'] == 'cpc'
    
    def test_utm_override_click_id(self):
        """Test that UTM parameters override click ID inference."""
        result = webmetic_referrer(
            url="https://site.com/?utm_source=newsletter&utm_medium=email&gclid=abc123"
        )
        
        # Should use UTM attribution, not Google
        assert result['source'] == 'newsletter'
        assert result['medium'] == 'email'
        
        # But should still include the click ID
        assert result['click_id'] == 'abc123'
        assert result['click_id_type'] == 'gclid'
    
    def test_social_media_platforms(self):
        """Test various social media click IDs."""
        test_cases = [
            ("https://site.com/?ttclid=tiktok123", "twitter", "cpc", "ttclid", "tiktok123"),
            ("https://site.com/?twclid=twitter456", "twitter", "cpc", "twclid", "twitter456"),
            ("https://site.com/?li_fat_id=linkedin789", "linkedin", "cpc", "li_fat_id", "linkedin789"),
            # Note: igshid is not a click ID, so it won't be in click_id field
            ("https://site.com/?igshid=instagram123", "instagram", "social", None, None),
        ]
        
        for url, expected_source, expected_medium, expected_click_id_type, expected_click_id in test_cases:
            result = webmetic_referrer(url)
            assert result['source'] == expected_source
            assert result['medium'] == expected_medium
            if expected_click_id_type:
                assert result['click_id_type'] == expected_click_id_type
                assert result['click_id'] == expected_click_id
            else:
                # Instagram share ID should still be in result as separate field
                assert result.get('click_id') is None
                assert result.get('click_id_type') is None
                assert 'igshid' in result
    
    def test_email_marketing(self):
        """Test email marketing parameters."""
        result = webmetic_referrer(
            url="https://site.com/?mc_cid=campaign123&mc_eid=email456"
        )
        
        assert result['source'] == 'mailchimp'
        assert result['medium'] == 'email'
        assert result['mc_cid'] == 'campaign123'
        assert result['mc_eid'] == 'email456'
        # Email marketing parameters are not click IDs
        assert result.get('click_id') is None
        assert result.get('click_id_type') is None
    
    def test_microsoft_ads(self):
        """Test Microsoft/Bing ads."""
        result = webmetic_referrer(
            url="https://site.com/?msclkid=microsoft123"
        )
        
        assert result['source'] == 'bing'
        assert result['medium'] == 'cpc'
        assert result['click_id'] == 'microsoft123'
        assert result['click_id_type'] == 'msclkid'
    
    def test_all_utm_parameters(self):
        """Test that all UTM parameters are included."""
        result = webmetic_referrer(
            url="https://site.com/?utm_source=test&utm_medium=social&utm_campaign=summer&utm_term=beach&utm_content=banner&utm_id=123"
        )
        
        assert result['utm_source'] == 'test'
        assert result['utm_medium'] == 'social'
        assert result['utm_campaign'] == 'summer'
        assert result['utm_term'] == 'beach'
        assert result['utm_content'] == 'banner'
        assert result['utm_id'] == '123'
    
    def test_clean_output_no_none_values(self):
        """Test that None values are filtered out."""
        result = webmetic_referrer("https://site.com/?utm_source=test")
        
        # Should only include non-None values
        for key, value in result.items():
            assert value is not None
    
    def test_malformed_url(self):
        """Test handling of malformed URLs."""
        result = webmetic_referrer("not-a-url")
        
        # Should handle gracefully
        assert result['source'] == '(direct)'
        assert result['medium'] == '(none)'
    
    def test_empty_url(self):
        """Test handling of empty URL."""
        result = webmetic_referrer("")
        
        assert result['source'] == '(direct)'
        assert result['medium'] == '(none)'
    
    def test_convenience_alias(self):
        """Test the 'referrer' convenience alias."""
        result1 = webmetic_referrer("https://site.com/?utm_source=test")
        result2 = referrer("https://site.com/?utm_source=test")
        
        # Should be identical
        assert result1 == result2
    
    def test_case_insensitive_utm(self):
        """Test case insensitive UTM parameter handling."""
        result = webmetic_referrer(
            url="https://site.com/?UTM_SOURCE=Google&Utm_Medium=CPC"
        )
        
        # UTM values now preserve case
        assert result['utm_source'] == 'Google'
        assert result['utm_medium'] == 'CPC'
    
    def test_preserve_click_id_case(self):
        """Test that click ID case is preserved."""
        result = webmetic_referrer(
            url="https://site.com/?gclid=CjwKCAiA_Base64_String"
        )
        
        # Should preserve original case for click IDs
        assert result['click_id'] == 'CjwKCAiA_Base64_String'
        assert result['click_id_type'] == 'gclid'
    
    def test_priority_order(self):
        """Test attribution priority order."""
        # UTM should override click ID inference
        result = webmetic_referrer(
            url="https://site.com/?utm_source=newsletter&utm_medium=email&fbclid=fb123"
        )
        
        assert result['source'] == 'newsletter'  # UTM takes priority
        assert result['medium'] == 'email'       # UTM takes priority
        assert result['click_id'] == 'fb123'     # Click ID is still included
        assert result['click_id_type'] == 'fbclid'
    
    def test_referrer_fallback(self):
        """Test fallback to referrer analysis when no URL parameters."""
        result = webmetic_referrer(
            url="https://site.com/blog",
            referrer="https://www.google.com/search?q=python+tutorial"
        )
        
        # Should use referrer analysis
        assert result['source'] == 'google'
        assert result['medium'] == 'organic'
        assert result['term'] == 'python tutorial'