#!/usr/bin/env python3
"""
Test script to verify the YouTube Sentiment Analyzer setup
"""

import sys
import os
from config import Config

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import requests
        print("✓ Requests imported successfully")
    except ImportError as e:
        print(f"✗ Requests import failed: {e}")
        return False
    
    try:
        from googleapiclient.discovery import build
        print("✓ Google API Client imported successfully")
    except ImportError as e:
        print(f"✗ Google API Client import failed: {e}")
        return False
    
    try:
        from langchain.llms import OpenAI
        print("✓ LangChain OpenAI imported successfully")
    except ImportError as e:
        print(f"✗ LangChain OpenAI import failed: {e}")
        return False
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✓ LangChain Google GenAI imported successfully")
    except ImportError as e:
        print(f"✗ LangChain Google GenAI import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        config = Config()
        print("✓ Configuration loaded successfully")
        
        # Check if YouTube API key is set
        if config.YOUTUBE_API_KEY and config.YOUTUBE_API_KEY != 'your_youtube_api_key_here':
            print("✓ YouTube API key is configured")
        else:
            print("⚠ YouTube API key not configured (will need to be set)")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_prompt_file():
    """Test if prompt.txt exists and is readable"""
    print("\nTesting prompt file...")
    
    try:
        if os.path.exists('prompt.txt'):
            with open('prompt.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 100:  # Basic check that file has content
                    print("✓ prompt.txt exists and contains content")
                    return True
                else:
                    print("⚠ prompt.txt exists but seems empty")
                    return False
        else:
            print("✗ prompt.txt not found")
            return False
    except Exception as e:
        print(f"✗ Error reading prompt.txt: {e}")
        return False

def test_flask_app():
    """Test if Flask app can be created"""
    print("\nTesting Flask app...")
    
    try:
        from app import app
        print("✓ Flask app created successfully")
        return True
    except Exception as e:
        print(f"✗ Flask app creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("YouTube Sentiment Analyzer - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_prompt_file,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Set your YouTube API key in environment variables")
        print("2. Run: python app.py")
        print("3. Open http://localhost:5000 in your browser")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check if prompt.txt exists in the project directory")
        print("3. Verify your Python version (3.8+ required)")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
