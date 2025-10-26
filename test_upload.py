#!/usr/bin/env python3
"""
Image Upload System - Backend Test Script

This script tests all the upload endpoints to ensure they work correctly.

Usage:
    python test_upload.py
"""

import requests
import os
from pathlib import Path

BASE_URL = "http://localhost:8000/api/upload"

def test_upload_endpoints():
    """Test all upload endpoints"""
    
    print("🧪 Testing AgroShield Image Upload System\n")
    print("=" * 60)
    
    # Create test image if not exists
    test_image = Path("test_image.jpg")
    if not test_image.exists():
        print("❌ Test image not found. Please create 'test_image.jpg' in the current directory.")
        return
    
    # Test 1: Upload generic photo
    print("\n1️⃣  Testing generic photo upload...")
    try:
        with open(test_image, 'rb') as f:
            files = {'photo': f}
            data = {'category': 'general'}
            response = requests.post(f"{BASE_URL}/photo", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Uploaded to: {result['url']}")
            print(f"   Filename: {result['filename']}")
            print(f"   Size: {result['size']} bytes")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Upload plant image
    print("\n2️⃣  Testing plant image upload...")
    try:
        with open(test_image, 'rb') as f:
            files = {'photo': f}
            response = requests.post(f"{BASE_URL}/plant", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Uploaded plant image: {result['url']}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Upload leaf image
    print("\n3️⃣  Testing leaf image upload...")
    try:
        with open(test_image, 'rb') as f:
            files = {'photo': f}
            response = requests.post(f"{BASE_URL}/leaf", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Uploaded leaf image: {result['url']}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Upload soil image
    print("\n4️⃣  Testing soil image upload...")
    try:
        with open(test_image, 'rb') as f:
            files = {'photo': f}
            response = requests.post(f"{BASE_URL}/soil", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Uploaded soil image: {result['url']}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Upload farm image
    print("\n5️⃣  Testing farm image upload...")
    try:
        with open(test_image, 'rb') as f:
            files = {'photo': f}
            response = requests.post(f"{BASE_URL}/farm", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Uploaded farm image: {result['url']}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Get upload statistics
    print("\n6️⃣  Testing upload statistics...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Success! Upload statistics:")
            print(f"   Total files: {stats['total']['files']}")
            print(f"   Total size: {stats['total']['size_mb']:.2f} MB")
            print("\n   By category:")
            for category, data in stats['categories'].items():
                if data['count'] > 0:
                    print(f"   - {category}: {data['count']} files ({data['size_mb']:.2f} MB)")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Testing complete!\n")
    print("Next steps:")
    print("1. Check the 'uploads' directory for uploaded files")
    print("2. Test the frontend ImageUploader component")
    print("3. Integrate with existing screens")


if __name__ == "__main__":
    print("\n📸 AgroShield Image Upload System - Backend Test\n")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/api/upload/stats", timeout=2)
        test_upload_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Backend server is not running!")
        print("\nPlease start the server first:")
        print("   cd backend")
        print("   uvicorn app.main:app --reload")
        print("\nThen run this test script again.")
    except Exception as e:
        print(f"❌ Error: {e}")
