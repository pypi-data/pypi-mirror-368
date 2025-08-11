#!/usr/bin/env python3
"""
Basic usage examples for utm-referrer-attribution-parser.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utm_referrer_parser import parse_attribution


def example_google_ads():
    """Example: Google Ads click with UTM parameters."""
    print("=== Google Ads Click Example ===")
    
    tracking_data = {
        "dl": "https://mysite.com/landing?utm_source=google&utm_medium=cpc&utm_campaign=winter_sale&gclid=CjwKCAiA",
        "dr": "https://www.google.com/aclk?sa=L&ai=...",
        "bu": "https://mysite.com",
        "timestamp": "2025-01-29T10:30:00",
        "ip_address": "85.123.45.67"
    }
    
    result = parse_attribution(tracking_data)
    
    print(f"UTM Source: {result.get('utm_source')}")
    print(f"UTM Medium: {result.get('utm_medium')}")
    print(f"UTM Campaign: {result.get('utm_campaign')}")
    print(f"Google Click ID: {result.get('gclid')}")
    print(f"Final Attribution: {result.get('attribution_source')} / {result.get('attribution_medium')}")
    print()


def example_facebook_ad():
    """Example: Facebook ad click."""
    print("=== Facebook Ad Click Example ===")
    
    tracking_data = {
        "dl": "https://mysite.com/product?fbclid=IwAR1234567890",
        "dr": "https://www.facebook.com/",
        "bu": "https://mysite.com",
    }
    
    result = parse_attribution(tracking_data)
    
    print(f"Facebook Click ID: {result.get('fbclid')}")
    print(f"Attribution Source: {result.get('attribution_source')}")
    print(f"Attribution Medium: {result.get('attribution_medium')}")
    print()


def example_organic_search():
    """Example: Organic Google search."""
    print("=== Organic Search Example ===")
    
    tracking_data = {
        "dl": "https://mysite.com/blog/analytics-guide",
        "dr": "https://www.google.com/search?q=web+analytics+guide",
        "bu": "https://mysite.com",
    }
    
    result = parse_attribution(tracking_data)
    
    print(f"Referrer Source: {result.get('referrer_source')}")
    print(f"Referrer Medium: {result.get('referrer_medium')}")
    print(f"Search Term: {result.get('referrer_term')}")
    print(f"Final Attribution: {result.get('attribution_source')} / {result.get('attribution_medium')}")
    print()


def example_direct_traffic():
    """Example: Direct traffic."""
    print("=== Direct Traffic Example ===")
    
    tracking_data = {
        "dl": "https://mysite.com/",
        "dr": "",  # Empty referrer
        "bu": "https://mysite.com",
    }
    
    result = parse_attribution(tracking_data)
    
    print(f"Attribution Source: {result.get('attribution_source')}")
    print(f"Attribution Medium: {result.get('attribution_medium')}")
    print()


def example_email_campaign():
    """Example: Email marketing campaign."""
    print("=== Email Campaign Example ===")
    
    tracking_data = {
        "dl": "https://mysite.com/newsletter-offer?utm_source=newsletter&utm_medium=email&utm_campaign=march2024&mc_cid=abc123",
        "dr": "https://mailchimp.com/",
        "bu": "https://mysite.com",
    }
    
    result = parse_attribution(tracking_data)
    
    print(f"UTM Source: {result.get('utm_source')}")
    print(f"UTM Medium: {result.get('utm_medium')}")
    print(f"UTM Campaign: {result.get('utm_campaign')}")
    print(f"Mailchimp Campaign ID: {result.get('mc_cid')}")
    print(f"Final Attribution: {result.get('attribution_source')} / {result.get('attribution_medium')}")
    print()


def example_mixed_parameters():
    """Example: Mixed tracking parameters."""
    print("=== Mixed Parameters Example ===")
    
    tracking_data = {
        "dl": "https://mysite.com/?utm_source=social&utm_medium=organic&fbclid=fb123&gclid=gc456",
        "dr": "https://www.facebook.com/",
        "bu": "https://mysite.com",
    }
    
    result = parse_attribution(tracking_data)
    
    print(f"UTM Source: {result.get('utm_source')}")
    print(f"UTM Medium: {result.get('utm_medium')}")
    print(f"Facebook Click ID: {result.get('fbclid')}")
    print(f"Google Click ID: {result.get('gclid')}")
    print(f"Final Attribution: {result.get('attribution_source')} / {result.get('attribution_medium')}")
    print("Note: UTM parameters take priority in attribution logic")
    print()


if __name__ == "__main__":
    print("utm-referrer-attribution-parser Usage Examples")
    print("=" * 50)
    print()
    
    example_google_ads()
    example_facebook_ad()
    example_organic_search()
    example_direct_traffic()
    example_email_campaign()
    example_mixed_parameters()
    
    print("For more examples and documentation, visit:")
    print("https://github.com/webmetic/utm-referrer-attribution-parser")