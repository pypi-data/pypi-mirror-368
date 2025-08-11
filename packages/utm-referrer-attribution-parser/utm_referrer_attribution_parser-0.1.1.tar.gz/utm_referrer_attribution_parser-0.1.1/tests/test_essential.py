"""Essential tests for production-ready utm-referrer-attribution-parser.

These tests cover the core business logic and common edge cases that matter
for real-world usage without excessive complexity.
"""

import pytest
from utm_referrer_parser import webmetic_referrer, parse_attribution


class TestCoreAttribution:
    """Tests for core attribution logic - the main business value."""

    def test_google_ads_complete_flow(self):
        """Test complete Google Ads attribution with all parameters."""
        result = webmetic_referrer(
            url="https://mysite.com/product?utm_source=google&utm_medium=cpc&utm_campaign=winter_sale&gclid=CjwKCAiA",
            referrer="https://www.google.com/aclk?sa=L&ai=..."
        )
        
        assert result['source'] == 'google'
        assert result['medium'] == 'cpc'
        assert result['campaign'] == 'winter_sale'
        assert result['click_id'] == 'CjwKCAiA'
        assert result['click_id_type'] == 'gclid'

    def test_facebook_ad_attribution(self):
        """Test Facebook ad click attribution."""
        result = webmetic_referrer(
            url="https://mysite.com/product?fbclid=IwAR1234567890",
            referrer="https://www.facebook.com/"
        )
        
        assert result['source'] == 'facebook'
        assert result['medium'] == 'cpc'
        assert result['click_id'] == 'IwAR1234567890'
        assert result['click_id_type'] == 'fbclid'

    def test_organic_search_with_term(self):
        """Test organic search with search term extraction."""
        result = webmetic_referrer(
            url="https://mysite.com/blog/analytics-guide",
            referrer="https://www.google.com/search?q=web+analytics+guide"
        )
        
        assert result['source'] == 'google'
        assert result['medium'] == 'organic'
        assert result['term'] == 'web analytics guide'

    def test_direct_traffic(self):
        """Test direct traffic attribution."""
        result = webmetic_referrer("https://mysite.com/")
        
        assert result['source'] == '(direct)'
        assert result['medium'] == '(none)'

    def test_utm_overrides_referrer(self):
        """Test that UTM parameters take priority over referrer analysis."""
        result = webmetic_referrer(
            url="https://mysite.com/?utm_source=newsletter&utm_medium=email&utm_campaign=march2024",
            referrer="https://www.google.com/search?q=test"
        )
        
        # UTM should take priority
        assert result['source'] == 'newsletter'
        assert result['medium'] == 'email'
        assert result['campaign'] == 'march2024'

    def test_click_id_priority_logic(self):
        """Test that Google click IDs take priority over other platforms."""
        result = webmetic_referrer(
            url="https://mysite.com/?gclid=google123&fbclid=facebook456"
        )
        
        # Google should take priority (first in CLICK_ID_PARAMETERS)
        assert result['click_id'] == 'google123'
        assert result['click_id_type'] == 'gclid'
        assert result['source'] == 'google'
        assert result['medium'] == 'cpc'


class TestTrackingParameters:
    """Tests for the 25+ supported tracking parameters."""

    def test_utm_parameters_complete(self):
        """Test all UTM parameters are extracted."""
        result = webmetic_referrer(
            "https://site.com/?utm_source=google&utm_medium=cpc&utm_campaign=summer&utm_term=analytics&utm_content=banner&utm_id=123"
        )
        
        assert result['utm_source'] == 'google'
        assert result['utm_medium'] == 'cpc'
        assert result['utm_campaign'] == 'summer'
        assert result['utm_term'] == 'analytics'
        assert result['utm_content'] == 'banner'
        assert result['utm_id'] == '123'

    def test_google_ads_parameters(self):
        """Test Google Ads specific parameters."""
        result = webmetic_referrer(
            "https://site.com/?gclid=abc&gclsrc=aw&gbraid=def&wbraid=ghi&gad_source=jkl"
        )
        
        # gclid should be in unified click_id field
        assert result['click_id'] == 'abc'
        assert result['click_id_type'] == 'gclid'
        # Other Google parameters should remain separate
        assert result['gclsrc'] == 'aw'
        assert result['gad_source'] == 'jkl'
        # gbraid and wbraid are also click IDs, but gclid has priority

    def test_social_media_parameters(self):
        """Test social media platform parameters."""
        # Facebook
        result = webmetic_referrer("https://site.com/?fbclid=fb123")
        assert result['click_id'] == 'fb123'
        assert result['click_id_type'] == 'fbclid'
        assert result['source'] == 'facebook'
        
        # Twitter (ttclid maps to Twitter in current implementation)
        result = webmetic_referrer("https://site.com/?ttclid=tt123")
        assert result['click_id'] == 'tt123'
        assert result['click_id_type'] == 'ttclid'
        assert result['source'] == 'twitter'
        
        # LinkedIn
        result = webmetic_referrer("https://site.com/?li_fat_id=li123")
        assert result['click_id'] == 'li123'
        assert result['click_id_type'] == 'li_fat_id'
        assert result['source'] == 'linkedin'

    def test_email_marketing_parameters(self):
        """Test email marketing platform parameters."""
        # Mailchimp
        result = webmetic_referrer("https://site.com/?mc_cid=campaign123&mc_eid=email456")
        assert result['mc_cid'] == 'campaign123'
        assert result['mc_eid'] == 'email456'
        assert result['source'] == 'mailchimp'
        assert result['medium'] == 'email'

    def test_microsoft_parameters(self):
        """Test Microsoft/Bing Ads parameters."""
        result = webmetic_referrer("https://site.com/?msclkid=bing123")
        assert result['click_id'] == 'bing123'
        assert result['click_id_type'] == 'msclkid'
        assert result['source'] == 'bing'
        assert result['medium'] == 'cpc'


class TestInputValidation:
    """Tests for handling common input issues that could break user apps."""

    def test_empty_and_none_inputs(self):
        """Test handling of empty and None inputs."""
        # Empty string
        result = webmetic_referrer("")
        assert result['source'] == '(direct)'
        assert result['medium'] == '(none)'
        
        # None input should be handled gracefully
        result = webmetic_referrer(None)
        assert isinstance(result, dict)
        assert 'source' in result
        assert 'medium' in result

    def test_malformed_urls_dont_crash(self):
        """Test that common malformed URLs don't crash the system."""
        malformed_urls = [
            "not-a-url",
            "http://",
            "https://",
            "javascript:alert('test')",
            "http://domain.com/?param=value%",  # Invalid URL encoding
        ]
        
        for url in malformed_urls:
            result = webmetic_referrer(url)
            assert isinstance(result, dict)
            assert 'source' in result
            assert 'medium' in result

    def test_non_string_inputs(self):
        """Test handling of non-string inputs."""
        # Integer input
        result = webmetic_referrer(123)
        assert isinstance(result, dict)
        
        # List input
        result = webmetic_referrer([])
        assert isinstance(result, dict)
        
        # Dict input  
        result = webmetic_referrer({})
        assert isinstance(result, dict)

    def test_unicode_support(self):
        """Test Unicode characters in campaign names."""
        result = webmetic_referrer(
            "https://example.com/?utm_source=测试&utm_medium=中文&utm_campaign=🚀"
        )
        
        assert result['utm_source'] == '测试'
        assert result['utm_medium'] == '中文'
        assert result['utm_campaign'] == '🚀'

    def test_url_encoding_edge_cases(self):
        """Test common URL encoding scenarios."""
        # Spaces encoded as %20
        result = webmetic_referrer("https://site.com/?utm_source=google%20ads")
        assert result['utm_source'] == 'google ads'
        
        # Plus signs (should be preserved in campaign names)
        result = webmetic_referrer("https://site.com/?utm_campaign=summer+sale")
        assert result['utm_campaign'] == 'summer+sale'  # Preserved intentionally
        
        # Mixed case parameters
        result = webmetic_referrer("https://site.com/?UTM_SOURCE=Google&Utm_Medium=CPC")
        assert result['utm_source'] == 'Google'  # Case preserved in values
        assert result['utm_medium'] == 'CPC'


class TestParseAttributionComplex:
    """Tests for the lower-level parse_attribution function."""

    def test_tracking_data_format(self):
        """Test parse_attribution with tracking data dictionary."""
        tracking_data = {
            "dl": "https://mysite.com/?utm_source=google&utm_medium=cpc",
            "dr": "https://www.google.com/search?q=test",
            "bu": "https://mysite.com",
            "timestamp": "2024-01-15T10:30:00",
            "user_id": "12345"
        }
        
        result = parse_attribution(tracking_data)
        
        # Should preserve original data
        assert result['timestamp'] == "2024-01-15T10:30:00"
        assert result['user_id'] == "12345"
        
        # Should add attribution
        assert result['attribution_source'] == 'google'
        assert result['attribution_medium'] == 'cpc'

    def test_invalid_tracking_data(self):
        """Test parse_attribution with invalid tracking data."""
        invalid_data = {
            "dl": None,
            "dr": 123,  # Non-string referrer
            "bu": ""
        }
        
        result = parse_attribution(invalid_data)
        assert isinstance(result, dict)
        assert 'attribution_source' in result
        assert 'attribution_medium' in result


class TestRealWorldScenarios:
    """Tests based on actual usage patterns from production systems."""

    def test_e_commerce_checkout(self):
        """Test e-commerce checkout attribution scenario."""
        result = webmetic_referrer(
            url="https://shop.com/checkout?utm_source=email&utm_medium=newsletter&utm_campaign=weekly_deals&mc_cid=campaign_123",
            referrer="https://mailchimp.com/redirect"
        )
        
        assert result['source'] == 'email'
        assert result['medium'] == 'newsletter'
        assert result['campaign'] == 'weekly_deals'
        assert result['mc_cid'] == 'campaign_123'

    def test_blog_post_from_social(self):
        """Test blog post attribution from social media."""
        result = webmetic_referrer(
            url="https://blog.example.com/how-to-analytics",
            referrer="https://www.facebook.com/some/post"
        )
        
        assert result['source'] == 'facebook'
        assert result['medium'] == 'social'

    def test_newsletter_campaign_complete(self):
        """Test complete newsletter campaign tracking."""
        result = webmetic_referrer(
            "https://site.com/landing?utm_source=newsletter&utm_medium=email&utm_campaign=march_2024&utm_content=header_cta&mc_cid=abc123"
        )
        
        assert result['source'] == 'newsletter'
        assert result['medium'] == 'email'
        assert result['campaign'] == 'march_2024'
        assert result['content'] == 'header_cta'
        assert result['mc_cid'] == 'abc123'

    def test_international_campaign(self):
        """Test international campaign with special characters."""
        result = webmetic_referrer(
            "https://site.com/?utm_source=café&utm_medium=français&utm_campaign=été_promotion"
        )
        
        assert result['utm_source'] == 'café'
        assert result['utm_medium'] == 'français'
        assert result['utm_campaign'] == 'été_promotion'

    def test_mobile_app_attribution(self):
        """Test attribution for mobile app deep links."""
        result = webmetic_referrer(
            "https://app.example.com/product?utm_source=instagram&utm_medium=social&fbclid=IwAR123"
        )
        
        # UTM should take priority
        assert result['source'] == 'instagram'
        assert result['medium'] == 'social'
        assert result['click_id'] == 'IwAR123'  # Click ID still preserved
        assert result['click_id_type'] == 'fbclid'