#!/usr/bin/env python3
"""
Test script to verify the educational chatbot installation
"""

import sys
import importlib

def test_python_version():
    """Test Python version"""
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print("✅ Python version OK")
    return True

def test_required_modules():
    """Test if required modules can be imported"""
    required_modules = [
        'flask',
        'pymysql',
        'bcrypt',
        'python-dotenv'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'python-dotenv':
                importlib.import_module('dotenv')
            else:
                importlib.import_module(module)
            print(f"✅ {module} - OK")
        except ImportError:
            print(f"❌ {module} - Missing")
            missing_modules.append(module)
    
    return len(missing_modules) == 0, missing_modules

def test_spacy():
    """Test spaCy installation"""
    try:
        import spacy
        print("✅ spaCy - OK")
        
        # Test if English model is available
        try:
            nlp = spacy.load('en_core_web_sm')
            print("✅ spaCy English model - OK")
            return True
        except OSError:
            print("❌ spaCy English model - Missing")
            print("   Run: python -m spacy download en_core_web_sm")
            return False
    except ImportError:
        print("❌ spaCy - Missing")
        return False

def test_database_config():
    """Test database configuration"""
    try:
        from config import Config
        print("✅ Configuration - OK")
        print(f"   Database: {Config.MYSQL_DB}")
        print(f"   Host: {Config.MYSQL_HOST}")
        print(f"   User: {Config.MYSQL_USER}")
        return True
    except Exception as e:
        print(f"❌ Configuration - Error: {e}")
        return False

def test_app_structure():
    """Test if app can be imported"""
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app creation - OK")
        return True
    except Exception as e:
        print(f"❌ Flask app creation - Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Educational Chatbot Installation")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("Required Modules", lambda: test_required_modules()[0]),
        ("spaCy", test_spacy),
        ("Database Config", test_database_config),
        ("App Structure", test_app_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} - Exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your installation looks good.")
        print("\n📝 Next steps:")
        print("1. Make sure XAMPP MySQL is running")
        print("2. Create the database using database_setup.sql")
        print("3. Run: python run.py")
    else:
        print("⚠️  Some tests failed. Please check the requirements.")
        
        # Show missing modules
        modules_ok, missing = test_required_modules()
        if not modules_ok:
            print(f"\n📦 Install missing modules:")
            print(f"   pip install {' '.join(missing)}")

if __name__ == "__main__":
    main()
