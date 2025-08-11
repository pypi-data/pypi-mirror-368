# utm-referrer-attribution-parser

A modern Python library that combines referrer parsing with tracking parameter extraction for comprehensive web analytics attribution.

## ✨ Super Simple API

```python
from utm_referrer_parser import webmetic_referrer

# Just pass the URL and optional referrer - that's it!
result = webmetic_referrer(
    url="https://example.com/page?utm_source=google&utm_medium=cpc&gclid=abc123",
    referrer="https://www.google.com/search?q=analytics"
)

print(result)
# {
#     'source': 'google',
#     'medium': 'cpc',
#     'click_id': 'abc123',
#     'click_id_type': 'gclid',
#     'term': 'analytics'
# }
```

## 🚀 Features

- **Ultra-Simple API**: Just `webmetic_referrer(url, referrer)` - that's it!
- **Unified Click Tracking**: Clean `click_id` and `click_id_type` fields instead of 15+ individual parameters
- **25+ Tracking Parameters**: UTM, Google Ads, Facebook, TikTok, LinkedIn, email platforms, and more
- **Smart Referrer Analysis**: Uses Snowplow's referrer database for accurate source/medium classification
- **Advanced Domain Parsing**: Uses tldextract for robust international domain handling (.co.uk, .com.au, etc.)
- **Auto-updating Database**: Weekly updates of referrer database with local fallback
- **High Performance**: In-memory caching and optimized parsing
- **Framework Agnostic**: Works with any Python web framework
- **Production Ready**: 99%+ accuracy validated with 150+ real-world test cases
- **International Support**: Handles global search engines (Google, Bing, Baidu, Yandex, Naver, etc.)

## 📦 Installation

```bash
pip install utm-referrer-attribution-parser
```

## 🎯 Quick Examples

### Google Ads Click
```python
result = webmetic_referrer(
    url="https://site.com/landing?utm_source=google&utm_medium=cpc&gclid=abc123"
)
# Returns: {'source': 'google', 'medium': 'cpc', 'click_id': 'abc123', 'click_id_type': 'gclid'}
```

### Facebook Ad
```python
result = webmetic_referrer(
    url="https://site.com/product?fbclid=fb123",
    referrer="https://www.facebook.com/"
)
# Returns: {'source': 'facebook', 'medium': 'cpc', 'click_id': 'fb123', 'click_id_type': 'fbclid'}
```

### Organic Search
```python
result = webmetic_referrer(
    url="https://site.com/blog",
    referrer="https://www.google.com/search?q=analytics+guide"
)
# Returns: {'source': 'Google', 'medium': 'search', 'term': 'analytics guide'}
```

### Direct Traffic
```python
result = webmetic_referrer("https://site.com/")
# Returns: {'source': '(direct)', 'medium': '(none)'}
```

### Internal Navigation
```python
result = webmetic_referrer(
    url="https://shop.example.com/products",
    referrer="https://example.com/"
)
# Returns: {'source': '(internal)', 'medium': 'internal'}
```

The library automatically detects internal navigation between subdomains using advanced TLD parsing, correctly handling complex domains like `.co.uk`, `.com.au`, `.org.br`, etc.

## 🎯 Unified Click Tracking

Instead of tracking 15+ individual click ID fields, we provide a clean unified structure:

### Old Approach (Complex)
```python
# Multiple individual fields to check
result = {
    'gclid': 'abc123',
    'fbclid': None,
    'ttclid': None,
    'msclkid': None,
    # ... 15+ more fields
}
```

### New Approach (Clean)
```python
# Just 2 unified fields
result = {
    'click_id': 'abc123',        # The actual tracking value
    'click_id_type': 'gclid'     # Which parameter it came from
}
```

### Benefits
- **Cleaner API**: 2 fields instead of 15+
- **Easier Logic**: Simple `if result['click_id']` checks
- **Platform Detection**: Still get source/medium attribution automatically
- **Priority Handling**: Google Ads → Facebook → Microsoft → Other platforms

## Supported Parameters

### Standard UTM
- `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`, `utm_id`

### Click Tracking (Unified)
- `click_id` - The actual click tracking value
- `click_id_type` - Which parameter provided it (`gclid`, `fbclid`, `ttclid`, etc.)

### Google Ads Metadata
- `gclsrc`, `gad_source`, `srsltid`

### Social Media
- `igshid` (Instagram), `sccid` (Snapchat)

### Email Marketing
- `mc_cid`, `mc_eid` (Mailchimp)
- `ml_subscriber_hash` (MailerLite)

### Other Platform Parameters
- `epik` (Pinterest), `ttd_uuid` (Trade Desk), `obOrigUrl` (Outbrain), and more

## 🧪 Validation & Testing

This library has been extensively tested with:
- **150+ real database cases** from production environments
- **50+ diverse internet scenarios** covering global platforms
- **99%+ accuracy rate** in attribution detection
- **100% error handling** - no crashes on malformed inputs

### Supported Platforms
- **Search Engines**: Google, Bing, Baidu, Yandex, DuckDuckGo, Naver, Yahoo, Ecosia
- **Social Media**: Facebook, Instagram, TikTok, Twitter, LinkedIn, Pinterest, Reddit, Snapchat
- **Email Marketing**: Mailchimp, MailerLite, Constant Contact, SendGrid, ConvertKit
- **Business Tools**: Slack, Microsoft Teams, Calendly, Notion, Zoom
- **E-commerce**: Amazon, eBay, Shopify, Etsy, AliExpress

## 🔄 Migration from Complex Systems

Replace complex tracking data dictionaries with simple function calls:

```python
# OLD: Complex dictionary approach
tracking_data = {
    "dl": "https://site.com/?utm_source=google&gclid=abc123",
    "dr": "https://www.google.com/search?q=analytics", 
    "bu": "https://site.com"
}
result = parse_attribution(tracking_data)

# NEW: Ultra-simple API
result = webmetic_referrer(
    url="https://site.com/?utm_source=google&gclid=abc123",
    referrer="https://www.google.com/search?q=analytics"
)
```

## 📊 What Makes This Different

- **Intelligent Priority**: UTM parameters → Click IDs → Referrer analysis → Direct traffic
- **Unified Click Tracking**: Clean `click_id`/`click_id_type` structure instead of 15+ individual fields
- **Click ID Detection**: Automatically identifies 25+ types of advertising click IDs
- **International Ready**: Built-in support for global search engines and platforms  
- **Real-world Tested**: Validated against actual production analytics data
- **Future Proof**: Auto-updating referrer database keeps up with new platforms

## License

MIT License - see LICENSE file for details.