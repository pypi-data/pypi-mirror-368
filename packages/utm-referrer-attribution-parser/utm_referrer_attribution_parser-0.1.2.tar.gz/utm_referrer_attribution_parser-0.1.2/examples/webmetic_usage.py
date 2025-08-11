#!/usr/bin/env python3
"""
Simple usage examples for webmetic_referrer() function.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utm_referrer_parser import webmetic_referrer


def example_google_ads():
    """Example: Google Ads click with UTM parameters."""
    print("=== Google Ads Click ===")
    
    result = webmetic_referrer(
        url="https://mysite.com/landing?utm_source=google&utm_medium=cpc&utm_campaign=winter_sale&gclid=CjwKCAiA",
        referrer="https://www.google.com/aclk?sa=L&ai=..."
    )
    
    print(f"Source: {result['source']}")
    print(f"Medium: {result['medium']}")
    print(f"Campaign: {result['campaign']}")
    print(f"Google Click ID: {result['gclid']}")
    print()


def example_facebook_ad():
    """Example: Facebook ad click - super simple!"""
    print("=== Facebook Ad Click ===")
    
    result = webmetic_referrer(
        url="https://mysite.com/product?fbclid=IwAR1234567890",
        referrer="https://www.facebook.com/"
    )
    
    print(f"Source: {result['source']}")
    print(f"Medium: {result['medium']}")
    print(f"Facebook Click ID: {result['fbclid']}")
    print()


def example_organic_search():
    """Example: Organic Google search."""
    print("=== Organic Search ===")
    
    result = webmetic_referrer(
        url="https://mysite.com/blog/analytics-guide",
        referrer="https://www.google.com/search?q=web+analytics+guide"
    )
    
    print(f"Source: {result['source']}")
    print(f"Medium: {result['medium']}")
    print(f"Search Term: {result['term']}")
    print()


def example_direct_traffic():
    """Example: Direct traffic - just one parameter!"""
    print("=== Direct Traffic ===")
    
    result = webmetic_referrer("https://mysite.com/")
    
    print(f"Source: {result['source']}")
    print(f"Medium: {result['medium']}")
    print()


def example_email_campaign():
    """Example: Email marketing campaign."""
    print("=== Email Campaign ===")
    
    result = webmetic_referrer(
        url="https://mysite.com/newsletter-offer?utm_source=newsletter&utm_medium=email&utm_campaign=march2024&mc_cid=abc123",
        referrer="https://mailchimp.com/"
    )
    
    print(f"Source: {result['source']}")
    print(f"Medium: {result['medium']}")
    print(f"Campaign: {result['campaign']}")
    print(f"Mailchimp Campaign ID: {result['mc_cid']}")
    print()


def example_multiple_click_ids():
    """Example: Multiple click IDs detected."""
    print("=== Multiple Click IDs ===")
    
    result = webmetic_referrer(
        url="https://mysite.com/?gclid=google123&fbclid=fb456&ttclid=tiktok789"
    )
    
    print(f"Source: {result['source']}")
    print(f"Medium: {result['medium']}")
    print("Detected Click IDs:")
    for key, value in result.items():
        if key.endswith('clid') or key.endswith('id'):
            print(f"  {key}: {value}")
    print()


def example_social_media():
    """Example: Various social media platforms."""
    print("=== Social Media Examples ===")
    
    platforms = [
        ("TikTok", "https://site.com/?ttclid=tiktok123", "https://tiktok.com"),
        ("Twitter", "https://site.com/?twclid=twitter456", "https://x.com"),
        ("LinkedIn", "https://site.com/?li_fat_id=linkedin789", "https://linkedin.com"),
        ("Instagram", "https://site.com/?igshid=instagram123", "https://instagram.com")
    ]
    
    for platform, url, referrer in platforms:
        result = webmetic_referrer(url, referrer)
        click_id_key = [k for k in result.keys() if k.endswith('id') or k.endswith('clid')][0]
        print(f"{platform}: {result['source']} / {result['medium']} (ID: {result[click_id_key]})")
    
    print()


def example_convenience_alias():
    """Example: Using the shorter 'referrer' alias."""
    print("=== Using Convenience Alias ===")
    
    from utm_referrer_parser import referrer  # Shorter alias!
    
    result = referrer(
        url="https://site.com/?utm_source=google&gclid=abc123",
        referrer="https://www.google.com/search"
    )
    
    print(f"Source: {result['source']} (using 'referrer' alias)")
    print()


if __name__ == "__main__":
    print("🚀 webmetic_referrer() - Simple Attribution Analysis")
    print("=" * 60)
    print()
    
    example_google_ads()
    example_facebook_ad()
    example_organic_search()
    example_direct_traffic()
    example_email_campaign()
    example_multiple_click_ids()
    example_social_media()
    example_convenience_alias()
    
    print("✨ Super simple API:")
    print("   webmetic_referrer(url, referrer)")
    print("   webmetic_referrer(url)  # referrer optional")
    print()
    print("🔗 GitHub: https://github.com/webmetic/utm-referrer-attribution-parser")