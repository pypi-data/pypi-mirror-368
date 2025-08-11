"""
utm-referrer-attribution-parser

A modern Python library that combines referrer parsing with tracking parameter 
extraction for comprehensive web analytics attribution.
"""

from .webmetic import webmetic_referrer, referrer
from .parser import parse_attribution

__version__ = "0.1.0"
__all__ = ["webmetic_referrer", "referrer", "parse_attribution"]
