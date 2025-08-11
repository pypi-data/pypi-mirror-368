# Changelog

All notable changes to utm-referrer-attribution-parser will be documented in this file.

## [0.1.2] - 2025-01-XX

### Added
- Advanced domain parsing using `tldextract` for robust international TLD support
- Comprehensive test suite for tldextract integration with 12+ new test cases
- Support for complex TLD scenarios (`.edu.au`, `.gov.br`, `.ac.uk`, etc.)
- Internal navigation detection between subdomains and root domains

### Changed  
- **BREAKING**: Added `tldextract>=3.1.0` as a new dependency
- Improved internal referrer detection using root domain comparison instead of exact hostname matching
- Enhanced referrer lookup efficiency - direct jump to root domain instead of recursive subdomain stripping
- Updated referrer parser to handle complex international domains correctly

### Fixed
- Fixed same-domain referrer detection bug where `bauma.de` → `exhibitors.bauma.de` was incorrectly classified as external referral
- Fixed subdomain navigation detection for complex TLDs (`.co.uk`, `.com.au`, etc.)
- Improved domain parsing accuracy for deeply nested subdomains

### Technical Improvements
- Replaced hardcoded TLD list with industry-standard `tldextract` library
- Optimized referrer database lookup performance for complex domains  
- Added fallback logic for edge cases where tldextract might fail
- Enhanced test coverage for international domain scenarios

## [0.1.1] - 2024-12-XX

### Changed
- Performance optimization for high-traffic scenarios
- Fix UTM source casing inconsistency and standardize search medium
- Implement unified click ID structure for cleaner API

## [0.1.0] - 2024-12-XX

### Added
- Initial release with UTM parameter extraction
- Referrer database integration using Snowplow data
- Support for 25+ tracking parameters
- Unified click ID tracking structure
- Auto-updating referrer database
- Comprehensive test suite with 150+ real-world cases