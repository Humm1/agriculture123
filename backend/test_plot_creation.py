"""
Test script to verify plot creation endpoint
"""
import requests
import json
from datetime import datetime

# API endpoint
BASE_URL = "https://urchin-app-86rjy.ondigitalocean.app"
# BASE_URL = "http://localhost:8000"  # Uncomment for local testing

def test_create_plot():
    """Test creating a plot without images"""
    
    print("Testing plot creation...")
    print("=" * 60)
    
    # Test data
    data = {
        "user_id": "test-user-123",  # Replace with actual user ID
        "crop_name": "Maize",
        "plot_name": "Test Plot 1",
        "planting_date": datetime.utcnow().isoformat(),
        "latitude": -1.2921,  # Nairobi coordinates
        "longitude": 36.8219,
        "area_size": 100.0,
        "notes": "Test plot creation",
        "soil_type": "Clay Loam"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/advanced-growth/plots/create-manual",
            data=data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: Plot created successfully!")
        else:
            print(f"\n❌ ERROR: Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_plot()
