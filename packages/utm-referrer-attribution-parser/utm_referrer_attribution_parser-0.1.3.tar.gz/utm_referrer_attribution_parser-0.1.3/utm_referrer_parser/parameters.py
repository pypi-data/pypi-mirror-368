"""
Comprehensive URL parameter extraction for tracking and attribution.

Supports all major tracking parameter types from various advertising and 
analytics platforms.
"""

from typing import Dict, List, Optional, Set
from urllib.parse import urlparse, parse_qsl
from .cache import get_parameter_extractor_cache


# Standard UTM parameters
UTM_PARAMETERS = {
    'utm_source',
    'utm_medium',
    'utm_campaign',
    'utm_term',
    'utm_content',
    'utm_id'
}

# Google Ads parameters
GOOGLE_ADS_PARAMETERS = {
    'gclid',      # Google Click ID
    'gclsrc',     # Google Click Source
    'gbraid',     # Google Ads - Enhanced Conversions
    'wbraid',     # Google Ads - Web to App
    'gad_source', # Google Ads Source
    'srsltid'     # Google Shopping
}

# Social Media parameters
SOCIAL_MEDIA_PARAMETERS = {
    'fbclid',     # Facebook Click ID
    'ttclid',     # TikTok Click ID
    'twclid',     # Twitter Click ID
    'li_fat_id',  # LinkedIn First-Party Ad Tracking
    'igshid',     # Instagram Share ID
    'ScCid'       # Snapchat Click ID
}

# Microsoft/Bing parameters
MICROSOFT_PARAMETERS = {
    'msclkid',    # Microsoft Click ID (Bing Ads)
}

# Email Marketing parameters
EMAIL_MARKETING_PARAMETERS = {
    'mc_cid',               # Mailchimp Campaign ID
    'mc_eid',               # Mailchimp Email ID
    'ml_subscriber_hash'    # MailerLite Subscriber Hash
}

# Other Platform parameters
OTHER_PLATFORM_PARAMETERS = {
    'dclid',       # DoubleClick Click ID
    'yclid',       # Yahoo Click ID
    'epik',        # Pinterest Enhanced Match
    'ttd_uuid',    # The Trade Desk UUID
    'rdt_cid',     # Reddit Click ID
    'obOrigUrl',   # Outbrain Original URL
    'obclick_id',  # Outbrain Click ID
    'tblci',       # Taboola Click ID
    'irclid',      # Impact Radius Click ID
    'tgWebAppStartParam'  # Telegram mini-app parameter
}

# Analytics/Attribution parameters
ANALYTICS_PARAMETERS = {
    'pk_campaign', # Piwik/Matomo Campaign
    'pk_source',   # Piwik/Matomo Source
    'pk_medium'    # Piwik/Matomo Medium
}

# Combine all parameter sets
ALL_TRACKING_PARAMETERS = (
    UTM_PARAMETERS |
    GOOGLE_ADS_PARAMETERS |
    SOCIAL_MEDIA_PARAMETERS |
    MICROSOFT_PARAMETERS |
    EMAIL_MARKETING_PARAMETERS |
    OTHER_PLATFORM_PARAMETERS |
    ANALYTICS_PARAMETERS
)


class ParameterExtractor:
    """Extracts tracking parameters from URLs."""

    def __init__(self, custom_parameters: Optional[Set[str]] = None) -> None:
        """
        Initialize parameter extractor.
        
        Args:
            custom_parameters: Additional custom parameters to extract
        """
        self.parameters = ALL_TRACKING_PARAMETERS.copy()
        if custom_parameters:
            self.parameters.update(custom_parameters)

    def extract_from_url(self, url: str) -> Dict[str, str]:
        """
        Extract all tracking parameters from a URL.
        
        Args:
            url: The URL to extract parameters from
            
        Returns:
            Dict of parameter names to values
        """
        # Handle non-string inputs gracefully
        if not url or not isinstance(url, str) or not url.strip():
            return {}

        # Check cache first
        cache = get_parameter_extractor_cache()
        cached_result = cache.get(url)
        if cached_result is not None:
            return cached_result

        try:
            parameters = {}

            # Parse query parameters from URL
            parsed_url = urlparse(url)
            if parsed_url.query:
                parameters.update(self._parse_query_string(parsed_url.query))

            # Parse fragment parameters (e.g., #utm_source=drift)
            # Skip fragments that start with '/' as they're likely SPA routes, not parameters
            if (parsed_url.fragment and ('=' in parsed_url.fragment) and
                not parsed_url.fragment.startswith('/')):
                parameters.update(self._parse_query_string(parsed_url.fragment))

            # Cache the result
            cache.put(url, parameters)
            return parameters

        except Exception:
            # Cache empty result to avoid repeated processing
            cache.put(url, {})
            return {}

    def _parse_query_string(self, query_string: str) -> Dict[str, str]:
        """
        Parse query string with improved error handling for malformed URLs.
        
        Args:
            query_string: The query string to parse
            
        Returns:
            Dict of parameter names to values
        """
        parameters = {}

        try:
            # Handle malformed URLs with multiple question marks
            # Split by '?' and process each part that contains '='
            parts = query_string.split('?')
            for part in parts:
                if '=' in part:
                    try:
                        # Detect separator type and parse accordingly
                        if ';' in part and '&' not in part:
                            # Pure semicolon separator
                            parsed_params = parse_qsl(part, keep_blank_values=True, separator=';')
                        else:
                            # Standard ampersand separator (default)
                            parsed_params = parse_qsl(part, keep_blank_values=True, separator='&')

                        for param, value in parsed_params:
                            param_lower = param.lower()

                            # Normalize parameter name (remove array notation like utm_source[])
                            normalized_param = param_lower.rstrip('[]').split('[')[0]

                            # Check if this is a tracked parameter
                            if normalized_param in {p.lower() for p in self.parameters}:
                                # Handle special cases that need custom decoding
                                if ('+' in part and param in part) or '%25' in part:
                                    # Find the original value in the query string for plus signs or double encoding
                                    import re
                                    pattern = rf'{re.escape(param)}=([^&]*)'
                                    match = re.search(pattern, part)
                                    if match:
                                        original_value = match.group(1)
                                        decoded_value = self._decode_parameter_value(original_value)
                                    else:
                                        decoded_value = self._decode_parameter_value(value)
                                else:
                                    # Standard case - just use the value from parse_qsl
                                    decoded_value = value

                                # Keep original case for parameter names, but normalize UTM params
                                if normalized_param.startswith('utm_'):
                                    # Don't force lowercase for UTM values to preserve campaign names
                                    parameters[normalized_param] = decoded_value if decoded_value else ''
                                else:
                                    # Keep original case for click IDs and other params
                                    parameters[normalized_param] = decoded_value if decoded_value else ''
                    except Exception:
                        # Continue processing other parts if one fails
                        continue
        except Exception:
            pass

        return parameters

    def _decode_parameter_value(self, value: str) -> str:
        """
        Properly decode URL parameter values with edge case handling.
        
        Args:
            value: The parameter value to decode
            
        Returns:
            Decoded parameter value
        """
        if not value:
            return ''

        try:
            from urllib.parse import unquote, unquote_plus

            # Handle double URL encoding (e.g., %252D -> %2D -> -)
            # For double-encoded values, decode twice to get the final readable value
            if '%25' in value:
                # This is double-encoded, decode twice
                decoded_once = unquote(value)
                # If it still contains encoded characters, decode again
                if '%' in decoded_once:
                    return unquote(decoded_once)
                else:
                    return decoded_once

            # For campaign names and other UTM parameters, be conservative with + signs
            # Many campaigns intentionally use + as part of the campaign name
            # Only convert + to space if there are clear space indicators
            if ('+' in value and
                not any(space_indicator in value for space_indicator in ['%20', '%2B']) and
                not value.count('+') > 3):  # Likely intentional + in campaign names
                # Use unquote to preserve + signs
                return unquote(value)
            else:
                # Use unquote_plus to convert + to spaces as normal
                return unquote_plus(value)

        except Exception:
            return value

    def extract_from_tracking_data(self, tracking_data: Dict[str, str]) -> Dict[str, str]:
        """
        Extract parameters from tracking data dictionary.
        
        Args:
            tracking_data: Dictionary containing URL fields (dl, dr, etc.)
            
        Returns:
            Dict of all extracted parameters
        """
        parameters = {}

        # Extract from destination URL (dl)
        if 'dl' in tracking_data:
            dest_url = tracking_data['dl']
            # Ensure destination URL is a string
            if isinstance(dest_url, str):
                dest_params = self.extract_from_url(dest_url)
                parameters.update(dest_params)

        # Extract from referrer URL (dr) - but don't override existing params
        if 'dr' in tracking_data:
            ref_url = tracking_data['dr']
            # Ensure referrer URL is a string
            if isinstance(ref_url, str):
                ref_params = self.extract_from_url(ref_url)
            else:
                ref_params = {}
            for key, value in ref_params.items():
                if key not in parameters:
                    parameters[key] = value

        return parameters

    def get_parameter_categories(self, parameters: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Categorize extracted parameters by their source/type.
        
        Args:
            parameters: Dictionary of extracted parameters
            
        Returns:
            Dict with parameter categories as keys and lists of param names as values
        """
        categories = {
            'utm': [],
            'google_ads': [],
            'social_media': [],
            'microsoft': [],
            'email_marketing': [],
            'analytics': [],
            'other': []
        }

        for param in parameters.keys():
            param_lower = param.lower()

            if param_lower in {p.lower() for p in UTM_PARAMETERS}:
                categories['utm'].append(param)
            elif param_lower in {p.lower() for p in GOOGLE_ADS_PARAMETERS}:
                categories['google_ads'].append(param)
            elif param_lower in {p.lower() for p in SOCIAL_MEDIA_PARAMETERS}:
                categories['social_media'].append(param)
            elif param_lower in {p.lower() for p in MICROSOFT_PARAMETERS}:
                categories['microsoft'].append(param)
            elif param_lower in {p.lower() for p in EMAIL_MARKETING_PARAMETERS}:
                categories['email_marketing'].append(param)
            elif param_lower in {p.lower() for p in ANALYTICS_PARAMETERS}:
                categories['analytics'].append(param)
            else:
                categories['other'].append(param)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}


def create_parameter_extractor(custom_parameters: Optional[Set[str]] = None) -> ParameterExtractor:
    """Create ParameterExtractor instance with optional custom parameters."""
    return ParameterExtractor(custom_parameters)
