"""
Main public API for webmetic-utm-referrer-attribution-parser.

Provides the simple, branded webmetic_referrer() function for easy attribution analysis.
"""

from typing import Dict, Optional
from .parser import parse_attribution


def webmetic_referrer(
    url: str, referrer: Optional[str] = None
) -> Dict[str, Optional[str]]:
    """
    Analyze URL and referrer to extract complete attribution data.

    This is the main function for webmetic-utm-referrer-attribution-parser.
    Simply pass a destination URL and optionally a referrer URL to get
    comprehensive attribution analysis including UTM parameters, click IDs,
    and intelligent source/medium detection.

    Args:
        url: Destination URL with potential tracking parameters
        referrer: Optional referrer URL for additional context

    Returns:
        Dictionary containing complete attribution data:

        Core Attribution:
        - source: Final attributed source (e.g., 'google', 'facebook', '(direct)')
        - medium: Final attributed medium (e.g., 'cpc', 'organic', 'social')
        - campaign: Campaign name from UTM parameters
        - term: Search term or UTM term
        - content: UTM content parameter

        Click Tracking (unified structure):
        - click_id: The actual click tracking value (or None if no click tracking)
        - click_id_type: Which parameter provided the click ID (or None)
        
        Other Tracking Parameters (only included if present):
        - All UTM parameters (utm_source, utm_medium, etc.)
        - Google Ads metadata: gclsrc, gad_source, srsltid  
        - Social Media: igshid, sccid
        - Email Marketing: mc_cid, mc_eid, ml_subscriber_hash
        - Other: epik, ttd_uuid, obOrigUrl, pk_campaign, etc.

    Examples:
        >>> # Google Ads click
        >>> result = webmetic_referrer(
        ...     url="https://site.com?utm_source=google&gclid=abc123",
        ...     referrer="https://www.google.com/aclk"
        ... )
        >>> print(result['source'])      # 'google'
        >>> print(result['click_id'])    # 'abc123'
        >>> print(result['click_id_type'])  # 'gclid'
        
        >>> # Facebook ad click
        >>> result = webmetic_referrer(
        ...     url="https://site.com?fbclid=IwAR123"
        ... )
        >>> print(result['source'])      # 'facebook'
        >>> print(result['click_id'])    # 'IwAR123'
        >>> print(result['click_id_type'])  # 'fbclid'

        >>> # Organic search (no click tracking)
        >>> result = webmetic_referrer(
        ...     url="https://site.com/blog",
        ...     referrer="https://www.google.com/search?q=analytics"
        ... )
        >>> print(result['source'])     # 'google'
        >>> print(result['term'])       # 'analytics'
        >>> print(result['click_id'])   # None

        >>> # Direct traffic (no referrer)
        >>> result = webmetic_referrer("https://site.com")
        >>> print(result['source'])  # '(direct)'
        >>> print(result['medium'])  # '(none)'
    """
    # Build tracking_data dictionary from simple parameters
    tracking_data = {
        "dl": url or "",
        "dr": referrer or "",
        "bu": _extract_base_url(url) if url else "",
    }

    # Use existing parse_attribution logic
    raw_result = parse_attribution(tracking_data)

    # Clean up and format the result for the public API
    return _format_webmetic_result(raw_result)


def _extract_base_url(url: str) -> str:
    """Extract base URL from full URL."""
    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return ""


# True click ID parameters (individual click tracking)
CLICK_ID_PARAMETERS = [
    # Google Ads (highest priority)
    "gclid",
    "gbraid", 
    "wbraid",
    # Major platforms
    "fbclid",
    "msclkid",
    "ttclid",
    "twclid", 
    "li_fat_id",
    # Other platforms
    "dclid",
    "yclid",
    "rdt_cid",
    "obclick_id",
    "tblci",
    "irclid"
]


def _format_webmetic_result(raw_result: Dict) -> Dict[str, Optional[str]]:
    """
    Format raw parse_attribution result into clean webmetic_referrer format.

    Focuses on the most important attribution data and includes all detected
    tracking parameters without the internal metadata.
    """
    result = {}

    # Core attribution (always present)
    result["source"] = raw_result.get("attribution_source")
    result["medium"] = raw_result.get("attribution_medium")
    result["campaign"] = raw_result.get("utm_campaign")
    result["term"] = (
        raw_result.get("attribution_term")
        or raw_result.get("utm_term")
        or raw_result.get("referrer_term")
    )
    result["content"] = raw_result.get("utm_content")
    result["id"] = raw_result.get("utm_id")

    # Find the first click ID parameter that exists (priority order)
    click_id = None
    click_id_type = None
    for param in CLICK_ID_PARAMETERS:
        if param in raw_result and raw_result[param]:
            click_id = raw_result[param]
            click_id_type = param
            break

    result["click_id"] = click_id
    result["click_id_type"] = click_id_type

    # Add other tracking parameters (non-click-ID parameters)
    tracking_params = [
        # UTM parameters
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "utm_id",
        # Google Ads metadata (not click IDs)
        "gclsrc",
        "gad_source", 
        "srsltid",
        # Social Media non-click parameters
        "igshid",
        "sccid",
        # Email Marketing (campaign/email identifiers, not click IDs)
        "mc_cid",
        "mc_eid",
        "ml_subscriber_hash",
        # Other Platforms
        "epik",
        "ttd_uuid",
        "obOrigUrl",
        # Analytics
        "pk_campaign",
        "pk_source",
        "pk_medium",
    ]

    # Only include tracking parameters that are actually present
    for param in tracking_params:
        if param in raw_result and raw_result[param]:
            result[param] = raw_result[param]

    # Remove None values for cleaner output
    return {k: v for k, v in result.items() if v is not None}


# Convenience alias for even shorter usage
referrer = webmetic_referrer
