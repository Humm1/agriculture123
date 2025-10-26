#!/usr/bin/env python3
"""
Test plot creation endpoint to diagnose database issue
"""
import requests
import json

# Test configuration
BASE_URL = "https://urchin-app-86rjy.ondigitalocean.app"
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"  # Test UUID

def test_plot_creation():
    """Test creating a plot with minimal data"""
    
    print("=" * 60)
    print("Testing Plot Creation Endpoint")
    print("=" * 60)
    
    # Prepare form data (multipart/form-data)
    form_data = {
        'user_id': TEST_USER_ID,
        'crop_name': 'Maize',
        'plot_name': 'Test Plot',
        'planting_date': '2025-10-26T12:00:00',
        'latitude': -1.2921,
        'longitude': 36.8219,
        'area_size': 100.0,
        'notes': 'Test plot creation',
        'soil_type': 'Clay Loam'
    }
    
    print("\n1. Testing endpoint without images...")
    print(f"URL: {BASE_URL}/api/advanced-growth/plots/create-manual")
    print(f"Data: {json.dumps(form_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/advanced-growth/plots/create-manual",
            data=form_data
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"\nResponse JSON:")
            print(json.dumps(response_data, indent=2))
            
            if response_data.get('success'):
                print("\n✅ SUCCESS: Plot created!")
                print(f"Plot ID: {response_data.get('plot_id')}")
            else:
                print("\n❌ FAILED: Plot not created")
                print(f"Error: {response_data.get('detail', 'Unknown error')}")
        except Exception as e:
            print(f"\n❌ Response is not JSON:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")

def test_db_endpoint():
    """Test database verification endpoint (if deployed)"""
    print("\n" + "=" * 60)
    print("Testing Database Verification Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/advanced-growth/db-test")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Endpoint not found - deployment not complete yet")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_plot_creation()
    test_db_endpoint()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
