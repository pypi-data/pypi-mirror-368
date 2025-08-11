"""
Main attribution parsing logic that combines parameter extraction 
and referrer analysis for comprehensive web analytics attribution.
"""

from typing import Dict, Optional, Any
from .parameters import create_parameter_extractor
from .referrers import create_referrer_parser

# Module-level singleton instances for high-performance scenarios
_referrer_parser = None
_parameter_extractor = None

def _get_referrer_parser():
    """Get cached referrer parser instance (singleton pattern for performance)."""
    global _referrer_parser
    if _referrer_parser is None:
        _referrer_parser = create_referrer_parser()
    return _referrer_parser

def _get_parameter_extractor():
    """Get cached parameter extractor instance (singleton pattern for performance)."""
    global _parameter_extractor
    if _parameter_extractor is None:
        _parameter_extractor = create_parameter_extractor()
    return _parameter_extractor


def parse_attribution(tracking_data: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    Parse tracking data and return complete attribution information.
    
    Combines URL parameter extraction and referrer analysis to provide
    comprehensive attribution data for web analytics.
    
    Args:
        tracking_data: Dictionary containing tracking information with keys:
            - dl: Destination URL (required)
            - dr: Referrer URL (optional)
            - bu: Base URL/Domain (optional)
            - Additional fields are preserved but not used for attribution
    
    Returns:
        Dictionary containing attribution information:
        - All extracted tracking parameters (utm_*, gclid, fbclid, etc.)
        - referrer_source: Source from referrer analysis
        - referrer_medium: Medium from referrer analysis  
        - referrer_term: Search term if available
        - attribution_source: Final attributed source
        - attribution_medium: Final attributed medium
        
    Examples:
        >>> tracking_data = {
        ...     "dl": "https://example.com?utm_source=google&utm_medium=cpc&gclid=abc123",
        ...     "dr": "https://www.google.com/search?q=test"
        ... }
        >>> result = parse_attribution(tracking_data)
        >>> print(result['utm_source'])  # 'google'
        >>> print(result['attribution_source'])  # 'google'
    """
    # Initialize result with all input data preserved
    result = tracking_data.copy()

    # Extract destination and referrer URLs - ensure they are strings
    destination_url = tracking_data.get('dl', '')
    referrer_url = tracking_data.get('dr', '')
    base_url = tracking_data.get('bu', '')

    # Convert to strings if not already
    if not isinstance(destination_url, str):
        destination_url = ''
    if not isinstance(referrer_url, str):
        referrer_url = ''
    if not isinstance(base_url, str):
        base_url = ''

    # Extract URL parameters
    param_extractor = _get_parameter_extractor()
    extracted_params = param_extractor.extract_from_tracking_data(tracking_data)
    result.update(extracted_params)

    # Parse referrer information
    referrer_parser = _get_referrer_parser()
    referrer_info = referrer_parser.parse(referrer_url, base_url)

    # Add referrer analysis results with prefix to avoid conflicts
    result['referrer_source'] = referrer_info['source']
    result['referrer_medium'] = referrer_info['medium']
    result['referrer_term'] = referrer_info.get('term')

    # Determine final attribution using intelligent logic
    attribution = _determine_attribution(extracted_params, referrer_info)
    result['attribution_source'] = attribution['source']
    result['attribution_medium'] = attribution['medium']

    # Add search term if available
    if attribution.get('term'):
        result['attribution_term'] = attribution['term']
    elif extracted_params.get('utm_term'):
        result['attribution_term'] = extracted_params['utm_term']
    elif referrer_info.get('term'):
        result['attribution_term'] = referrer_info['term']

    return result


def _determine_attribution(
    url_params: Dict[str, str],
    referrer_info: Dict[str, Optional[str]]
) -> Dict[str, Optional[str]]:
    """
    Intelligently determine final attribution based on URL parameters and referrer.
    
    Priority logic:
    1. If UTM parameters exist, use them (explicit campaign tracking)
    2. If click ID parameters exist, infer source/medium from them
    3. Fall back to referrer analysis
    4. Default to direct/(none) if nothing else available
    """
    attribution = {'source': None, 'medium': None, 'term': None}

    # Priority 1: Explicit UTM parameters (handle empty values gracefully)
    utm_source = url_params.get('utm_source', '').strip()
    utm_medium = url_params.get('utm_medium', '').strip()

    # If we have valid UTM parameters, use them
    if utm_source and utm_medium:
        attribution['source'] = utm_source.lower()
        attribution['medium'] = utm_medium
        attribution['term'] = url_params.get('utm_term')
        return attribution

    # If we have UTM source but no medium, check if click IDs can infer medium
    if utm_source and not utm_medium:
        click_id_attribution = _infer_from_click_ids(url_params)
        if click_id_attribution['source']:
            # Use UTM source but infer medium from click ID
            attribution['source'] = utm_source.lower()
            attribution['medium'] = click_id_attribution['medium']
            attribution['term'] = url_params.get('utm_term')
            return attribution
        else:
            # No click ID, default to (none) for medium
            attribution['source'] = utm_source.lower()
            attribution['medium'] = '(none)'
            attribution['term'] = url_params.get('utm_term')
            return attribution

    # If we have UTM medium but no source (or empty source), try to use referrer for source
    if utm_medium and not utm_source and referrer_info['source'] and referrer_info['source'] != '(direct)':
        attribution['source'] = referrer_info['source']
        attribution['medium'] = utm_medium
        attribution['term'] = url_params.get('utm_term') or referrer_info.get('term')
        return attribution

    # Priority 2: Special platform parameters (like Telegram)
    special_attribution = _parse_special_parameters(url_params)
    if special_attribution['source']:
        attribution['source'] = special_attribution['source']
        attribution['medium'] = special_attribution['medium']
        attribution['term'] = url_params.get('utm_term')
        return attribution

    # Priority 3: Click ID parameter inference
    click_id_attribution = _infer_from_click_ids(url_params)
    if click_id_attribution['source']:
        # Merge with any explicit UTM data
        if url_params.get('utm_source'):
            attribution['source'] = url_params['utm_source'].lower()
        else:
            attribution['source'] = click_id_attribution['source']

        if url_params.get('utm_medium'):
            attribution['medium'] = url_params['utm_medium']
        else:
            attribution['medium'] = click_id_attribution['medium']

        attribution['term'] = url_params.get('utm_term')
        return attribution

    # Priority 4: Referrer analysis
    if referrer_info['source'] and referrer_info['source'] != '(direct)':
        attribution['source'] = referrer_info['source']
        attribution['medium'] = referrer_info['medium']
        attribution['term'] = referrer_info.get('term')
        return attribution

    # Priority 5: Default to direct traffic
    attribution['source'] = '(direct)'
    attribution['medium'] = '(none)'
    return attribution


def _infer_from_click_ids(url_params: Dict[str, str]) -> Dict[str, Optional[str]]:
    """Infer source and medium from click ID parameters."""
    attribution = {'source': None, 'medium': None}

    # Google Ads click IDs
    google_click_ids = {'gclid', 'gbraid', 'wbraid', 'gad_source', 'srsltid'}
    if any(param in url_params for param in google_click_ids):
        attribution['source'] = 'google'
        attribution['medium'] = 'cpc'
        return attribution

    # Facebook click ID
    if 'fbclid' in url_params:
        attribution['source'] = 'facebook'
        attribution['medium'] = 'cpc'
        return attribution

    # Microsoft/Bing click ID
    if 'msclkid' in url_params:
        attribution['source'] = 'bing'
        attribution['medium'] = 'cpc'
        return attribution

    # Twitter click ID
    if 'twclid' in url_params or 'ttclid' in url_params:
        attribution['source'] = 'twitter'
        attribution['medium'] = 'cpc'
        return attribution

    # LinkedIn click ID
    if 'li_fat_id' in url_params:
        attribution['source'] = 'linkedin'
        attribution['medium'] = 'cpc'
        return attribution

    # TikTok click ID
    if 'ttclid' in url_params:
        attribution['source'] = 'tiktok'
        attribution['medium'] = 'cpc'
        return attribution

    # Instagram share ID
    if 'igshid' in url_params:
        attribution['source'] = 'instagram'
        attribution['medium'] = 'social'
        return attribution

    # Snapchat click ID
    if 'sccid' in url_params:
        attribution['source'] = 'snapchat'
        attribution['medium'] = 'cpc'
        return attribution

    # Email marketing platforms
    if 'mc_cid' in url_params or 'mc_eid' in url_params:
        attribution['source'] = 'mailchimp'
        attribution['medium'] = 'email'
        return attribution

    if 'ml_subscriber_hash' in url_params:
        attribution['source'] = 'mailerlite'
        attribution['medium'] = 'email'
        return attribution

    # Other platforms
    if 'dclid' in url_params:
        attribution['source'] = 'doubleclick'
        attribution['medium'] = 'display'
        return attribution

    if 'yclid' in url_params:
        attribution['source'] = 'yahoo'
        attribution['medium'] = 'cpc'
        return attribution

    if 'epik' in url_params:
        attribution['source'] = 'pinterest'
        attribution['medium'] = 'social'
        return attribution

    if 'rdt_cid' in url_params:
        attribution['source'] = 'reddit'
        attribution['medium'] = 'cpc'
        return attribution

    return attribution


def _parse_special_parameters(url_params: Dict[str, str]) -> Dict[str, Optional[str]]:
    """Parse special platform parameters that don't follow standard UTM format."""
    attribution = {'source': None, 'medium': None}

    # Telegram mini-app parameter (special format)
    if 'tgwebappstartparam' in url_params:
        tg_param = url_params['tgwebappstartparam']
        # Parse format like "utm_source-telegram_utm_medium-cpc"
        if 'utm_source-' in tg_param and 'utm_medium-' in tg_param:
            # Extract source and medium using string parsing
            import re

            # Extract source after "utm_source-"
            source_match = re.search(r'utm_source-([^_]+)', tg_param)
            medium_match = re.search(r'utm_medium-([^_]+)', tg_param)

            if source_match and medium_match:
                source = source_match.group(1)
                medium = medium_match.group(1)
                attribution['source'] = source
                attribution['medium'] = medium
                return attribution

    return attribution
