"""
Tests specifically for tldextract improvements in domain parsing.

This module tests the enhanced domain parsing capabilities introduced
with tldextract for both internal navigation detection and referrer lookup efficiency.
"""

import pytest
from utm_referrer_parser.referrers import ReferrerParser


class TestTldextractReferrerLookup:
    """Test improved referrer lookup efficiency with tldextract."""
    
    def setup_method(self):
        """Set up test data with complex TLD domains."""
        self.test_data = {
            'search': {
                'Google': {
                    'domains': [
                        'google.com', 'www.google.com',
                        'google.co.uk', 'www.google.co.uk', 
                        'google.com.au', 'www.google.com.au',
                        'google.co.jp', 'www.google.co.jp',
                        'google.org.br', 'www.google.org.br',
                    ],
                    'parameters': ['q']
                },
                'Yahoo': {
                    'domains': [
                        'yahoo.com', 'search.yahoo.com',
                        'yahoo.co.uk', 'uk.search.yahoo.com',
                        'yahoo.com.au', 'au.search.yahoo.com',
                    ],
                    'parameters': ['q', 'p']
                }
            },
            'social': {
                'Facebook': {
                    'domains': ['facebook.com', 'www.facebook.com', 'm.facebook.com']
                }
            }
        }
        self.parser = ReferrerParser(self.test_data)
    
    def test_direct_domain_matches(self):
        """Test that direct domain matches work correctly."""
        test_cases = [
            ('google.com', 'Google'),
            ('www.google.co.uk', 'Google'),
            ('yahoo.com.au', 'Yahoo'),
            ('facebook.com', 'Facebook'),
        ]
        
        for hostname, expected_name in test_cases:
            result = self.parser._lookup_referrer(hostname)
            assert result is not None, f"Should find match for {hostname}"
            assert result['name'] == expected_name, f"Wrong name for {hostname}"
    
    def test_subdomain_fallback_efficiency(self):
        """Test that subdomain fallback jumps directly to root domain."""
        test_cases = [
            # Complex TLD cases that should jump directly to root
            ('images.google.co.uk', 'Google'),
            ('deep.subdomain.google.com.au', 'Google'),  
            ('cdn.assets.yahoo.co.uk', 'Yahoo'),
            ('mobile.m.facebook.com', 'Facebook'),
            # Very deep nesting
            ('a.b.c.d.e.google.org.br', 'Google'),
        ]
        
        for hostname, expected_name in test_cases:
            result = self.parser._lookup_referrer(hostname)
            assert result is not None, f"Should find match for {hostname}"
            assert result['name'] == expected_name, f"Wrong name for {hostname}"
    
    def test_unknown_domains_with_complex_tlds(self):
        """Test that unknown domains with complex TLDs are handled correctly."""
        test_cases = [
            'unknown.co.uk',
            'mystery.com.au', 
            'random.org.br',
            'deep.subdomain.unknown.edu.au',
        ]
        
        for hostname in test_cases:
            result = self.parser._lookup_referrer(hostname)
            assert result is None, f"Should not find match for unknown domain {hostname}"
    
    def test_mixed_case_handling(self):
        """Test that mixed case domains are handled correctly."""
        test_cases = [
            ('GOOGLE.CO.UK', 'Google'),
            ('Images.Google.COM.AU', 'Google'),
            ('Deep.Subdomain.YAHOO.co.uk', 'Yahoo'),
        ]
        
        for hostname, expected_name in test_cases:
            result = self.parser._lookup_referrer(hostname)
            assert result is not None, f"Should find match for {hostname}"
            assert result['name'] == expected_name, f"Wrong name for {hostname}"


class TestTldextractDomainExtraction:
    """Test the _get_root_domain method with tldextract."""
    
    def setup_method(self):
        """Set up a parser instance."""
        self.parser = ReferrerParser({})
    
    def test_simple_domains(self):
        """Test simple domain extraction."""
        test_cases = [
            ('example.com', 'example.com'),
            ('test.org', 'test.org'),
            ('site.net', 'site.net'),
        ]
        
        for hostname, expected in test_cases:
            result = self.parser._get_root_domain(hostname)
            assert result == expected, f"Wrong root domain for {hostname}"
    
    def test_complex_tlds(self):
        """Test complex TLD extraction."""
        test_cases = [
            ('example.co.uk', 'example.co.uk'),
            ('test.com.au', 'test.com.au'),
            ('site.org.br', 'site.org.br'),
            ('company.edu.au', 'company.edu.au'),
            ('gov.gov.uk', 'gov.gov.uk'),
            ('service.co.za', 'service.co.za'),
        ]
        
        for hostname, expected in test_cases:
            result = self.parser._get_root_domain(hostname)
            assert result == expected, f"Wrong root domain for {hostname}"
    
    def test_subdomain_extraction(self):
        """Test subdomain extraction to root domain."""
        test_cases = [
            ('www.example.com', 'example.com'),
            ('blog.example.co.uk', 'example.co.uk'),
            ('api.test.com.au', 'test.com.au'),
            ('cdn.assets.site.org.br', 'site.org.br'),
            ('deep.nested.company.edu.au', 'company.edu.au'),
        ]
        
        for hostname, expected in test_cases:
            result = self.parser._get_root_domain(hostname)
            assert result == expected, f"Wrong root domain for {hostname}"
    
    def test_very_deep_nesting(self):
        """Test very deeply nested subdomains."""
        test_cases = [
            ('a.b.c.d.e.f.example.com', 'example.com'),
            ('level1.level2.level3.test.co.uk', 'test.co.uk'),
            ('deep.very.nested.site.com.au', 'site.com.au'),
        ]
        
        for hostname, expected in test_cases:
            result = self.parser._get_root_domain(hostname)
            assert result == expected, f"Wrong root domain for {hostname}"
    
    def test_edge_cases(self):
        """Test edge cases and fallback behavior."""
        test_cases = [
            ('localhost', 'localhost'),
            ('example', 'example'),
            ('', None),
            (None, None),
        ]
        
        for hostname, expected in test_cases:
            result = self.parser._get_root_domain(hostname)
            assert result == expected, f"Wrong result for edge case {hostname}"
    
    def test_case_insensitivity(self):
        """Test that domain extraction is case insensitive."""
        test_cases = [
            ('EXAMPLE.COM', 'example.com'),
            ('Blog.EXAMPLE.CO.UK', 'example.co.uk'),
            ('API.Test.COM.AU', 'test.com.au'),
        ]
        
        for hostname, expected in test_cases:
            result = self.parser._get_root_domain(hostname)
            assert result == expected, f"Wrong root domain for {hostname}"


class TestTldextractIntegration:
    """Test integration between tldextract improvements and main functionality."""
    
    def test_internal_navigation_performance(self):
        """Test that internal navigation detection is working efficiently."""
        from utm_referrer_parser import webmetic_referrer
        
        # Test cases that would be slow with old recursive logic
        test_cases = [
            ('https://very.deep.nested.example.co.uk/page', 'https://example.co.uk/', 'Should be fast with tldextract'),
            ('https://a.b.c.d.e.site.com.au/api', 'https://site.com.au/', 'Deep nesting should be handled efficiently'),
        ]
        
        for url, referrer, description in test_cases:
            result = webmetic_referrer(url=url, referrer=referrer)
            assert result['source'] == '(internal)', f"Failed for {description}"
            assert result['medium'] == 'internal', f"Failed for {description}"
    
    def test_referrer_lookup_accuracy(self):
        """Test that referrer lookup is more accurate with tldextract."""
        from utm_referrer_parser import webmetic_referrer
        
        # Test that tldextract improvements allow proper referrer detection
        # Using known domains from the referrer database
        test_cases = [
            ('https://example.com/page', 'https://www.google.com/search?q=test', 'google', 'organic'),
            ('https://site.com/blog', 'https://www.facebook.com/some-post', 'facebook', 'social'),
        ]
        
        for url, referrer, expected_source, expected_medium in test_cases:
            result = webmetic_referrer(url=url, referrer=referrer)
            assert result['source'] == expected_source, f"Wrong source for {referrer}"
            assert result['medium'] == expected_medium, f"Wrong medium for {referrer}"