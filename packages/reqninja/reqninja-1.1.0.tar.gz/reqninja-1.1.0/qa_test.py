#!/usr/bin/env python3
"""
ReqNinja QA Test Suite
Comprehensive testing of all functionality
"""

import sys
import traceback
from pathlib import Path

def test_package_import():
    """Test basic package import"""
    try:
        import reqninja
        print("✅ Package import: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ Package import: FAILED - {e}")
        return False

def test_version():
    """Test version detection"""
    try:
        import reqninja
        version = getattr(reqninja, '__version__', 'Unknown')
        print(f"✅ Version check: SUCCESS - v{version}")
        return True
    except Exception as e:
        print(f"❌ Version check: FAILED - {e}")
        return False

def test_main_imports():
    """Test main function imports"""
    try:
        from reqninja import get, post, put, delete, ReqNinjaClient, Config
        print("✅ Main imports: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ Main imports: FAILED - {e}")
        return False

def test_client_creation():
    """Test client instantiation"""
    try:
        import reqninja
        client = reqninja.ReqNinjaClient()
        print("✅ Client creation: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ Client creation: FAILED - {e}")
        return False

def test_config_system():
    """Test configuration system"""
    try:
        from reqninja import Config
        config = Config()
        print(f"✅ Config system: SUCCESS - {config.config_path}")
        return True
    except Exception as e:
        print(f"❌ Config system: FAILED - {e}")
        return False

def test_http_get():
    """Test HTTP GET functionality"""
    try:
        import reqninja
        response = reqninja.get('https://httpbin.org/status/200', timeout=10)
        if response.status_code == 200:
            print("✅ HTTP GET: SUCCESS")
            return True
        else:
            print(f"❌ HTTP GET: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ HTTP GET: FAILED - {e}")
        return False

def test_http_post():
    """Test HTTP POST functionality"""
    try:
        import reqninja
        data = {"test": "data", "qa": True}
        response = reqninja.post('https://httpbin.org/post', json=data, timeout=10)
        if response.status_code == 200:
            print("✅ HTTP POST: SUCCESS")
            return True
        else:
            print(f"❌ HTTP POST: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ HTTP POST: FAILED - {e}")
        return False

def main():
    """Run all QA tests"""
    print("🧪 ReqNinja QA Test Suite")
    print("=" * 50)
    
    tests = [
        test_package_import,
        test_version,
        test_main_imports,
        test_client_creation,
        test_config_system,
        test_http_get,
        test_http_post,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: CRITICAL ERROR - {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"🎯 QA Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! ReqNinja is ready for production!")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
