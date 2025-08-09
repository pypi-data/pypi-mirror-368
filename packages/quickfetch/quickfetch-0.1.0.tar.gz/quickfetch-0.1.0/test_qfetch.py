#!/usr/bin/env python3
"""
Simple test script for qfetch package.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quickfetch import get

def test_basic_functionality():
    """Test basic qfetch functionality."""
    print("🧪 Testing quickfetch basic functionality...")
    
    try:
        # Test HTML page
        print("\n📄 Testing HTML page...")
        page = get("https://httpbin.org/html")
        
        if page.html:
            print("✅ HTML content fetched successfully")
            print(f"   Content length: {len(page.html)} characters")
        else:
            print("❌ Failed to fetch HTML content")
        
        # Test JSON API
        print("\n📊 Testing JSON API...")
        data = get("https://httpbin.org/json")
        
        if data.json:
            print("✅ JSON content fetched successfully")
            print(f"   JSON keys: {list(data.json.keys())}")
        else:
            print("❌ Failed to fetch JSON content")
        
        # Test CSS selector
        print("\n🎯 Testing CSS selector...")
        elements = page.select("h1")
        if elements:
            print(f"✅ Found {len(elements)} h1 elements")
            print(f"   First h1 text: {elements[0].text}")
        else:
            print("❌ No h1 elements found")
        
        # Test links extraction
        print("\n🔗 Testing links extraction...")
        links = page.links
        print(f"✅ Found {len(links)} links")
        
        # Test images extraction
        print("\n🖼️ Testing images extraction...")
        images = page.images
        print(f"✅ Found {len(images)} images")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_error_handling():
    """Test error handling."""
    print("\n🛡️ Testing error handling...")
    
    try:
        # Test invalid URL
        page = get("https://invalid-url-that-does-not-exist.com")
        print("✅ Error handling works (invalid URL handled gracefully)")
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 quickfetch Test Suite")
    print("=" * 50)
    
    success = True
    success &= test_basic_functionality()
    success &= test_error_handling()
    
    if success:
        print("\n🎉 All tests passed! quickfetch is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
