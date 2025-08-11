#!/usr/bin/env python3
"""
Local installation test script.
Run this after installing your package locally to verify it works.
"""

import sys

def test_basic_imports():
    """Test that all imports work correctly."""
    print("🧪 Testing imports...")
    try:
        from utm_referrer_parser import webmetic_referrer, parse_attribution
        print("✅ Main imports successful")
        
        # Test internal imports
        from utm_referrer_parser.parameters import create_parameter_extractor
        from utm_referrer_parser.referrers import create_referrer_parser
        print("✅ Internal imports successful")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test core functionality works."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from utm_referrer_parser import webmetic_referrer
        
        # Test Google Ads
        result = webmetic_referrer(
            url="https://mysite.com/?utm_source=google&utm_medium=cpc&gclid=abc123",
            referrer="https://www.google.com/aclk"
        )
        
        assert result['source'] == 'google'
        assert result['medium'] == 'cpc'
        assert result['click_id'] == 'abc123'
        assert result['click_id_type'] == 'gclid'
        print("✅ Google Ads attribution working")
        
        # Test Facebook
        result = webmetic_referrer("https://mysite.com/?fbclid=fb123")
        assert result['source'] == 'facebook'
        assert result['click_id'] == 'fb123'
        assert result['click_id_type'] == 'fbclid'
        print("✅ Facebook attribution working")
        
        # Test organic search
        result = webmetic_referrer(
            url="https://mysite.com/blog",
            referrer="https://www.google.com/search?q=analytics"
        )
        assert result['source'] == 'google'
        assert result['medium'] == 'organic'
        assert result['term'] == 'analytics'
        print("✅ Organic search attribution working")
        
        # Test direct traffic
        result = webmetic_referrer("https://mysite.com")
        assert result['source'] == '(direct)'
        assert result['medium'] == '(none)'
        print("✅ Direct traffic attribution working")
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False
    
    return True

def test_error_handling():
    """Test that error handling works."""
    print("\n🧪 Testing error handling...")
    
    try:
        from utm_referrer_parser import webmetic_referrer
        
        # Test malformed URLs
        result = webmetic_referrer("not-a-url")
        assert isinstance(result, dict)
        print("✅ Malformed URL handled gracefully")
        
        # Test None input
        result = webmetic_referrer(None)
        assert isinstance(result, dict)
        print("✅ None input handled gracefully")
        
        # Test empty string
        result = webmetic_referrer("")
        assert isinstance(result, dict)
        print("✅ Empty string handled gracefully")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    return True

def test_unicode_support():
    """Test Unicode character support."""
    print("\n🧪 Testing Unicode support...")
    
    try:
        from utm_referrer_parser import webmetic_referrer
        
        # Test Unicode in campaign names
        result = webmetic_referrer(
            "https://site.com/?utm_source=测试&utm_medium=中文&utm_campaign=🚀"
        )
        
        assert result['utm_source'] == '测试'
        assert result['utm_medium'] == '中文'  
        assert result['utm_campaign'] == '🚀'
        print("✅ Unicode characters working")
        
    except Exception as e:
        print(f"❌ Unicode test failed: {e}")
        return False
    
    return True

def test_parse_attribution_format():
    """Test the lower-level parse_attribution function."""
    print("\n🧪 Testing parse_attribution function...")
    
    try:
        from utm_referrer_parser import parse_attribution
        
        tracking_data = {
            "dl": "https://mysite.com/?utm_source=newsletter&utm_medium=email", 
            "dr": "https://mailchimp.com/",
            "bu": "https://mysite.com",
            "user_id": "12345"  # Custom data should be preserved
        }
        
        result = parse_attribution(tracking_data)
        
        # Check attribution
        assert result['attribution_source'] == 'newsletter'
        assert result['attribution_medium'] == 'email'
        
        # Check original data preserved
        assert result['user_id'] == '12345'
        
        print("✅ parse_attribution working correctly")
        
    except Exception as e:
        print(f"❌ parse_attribution test failed: {e}")
        return False
    
    return True

def main():
    """Run all local installation tests."""
    print("🚀 Testing Local Installation of utm-referrer-attribution-parser")
    print("=" * 70)
    
    tests = [
        test_basic_imports,
        test_basic_functionality, 
        test_error_handling,
        test_unicode_support,
        test_parse_attribution_format
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("⚠️  Some functionality may not be working correctly")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your local installation is working perfectly.")
        print("\n📋 Ready for:")
        print("   • Publishing to PyPI")
        print("   • Production deployment") 
        print("   • Integration into other projects")
    else:
        print("❌ Some tests failed. Please check the installation.")
        sys.exit(1)

if __name__ == "__main__":
    main()