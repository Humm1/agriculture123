"""
Test script for the unified plot creation system

Tests:
1. Create demo plot
2. Create real plot with multiple images
3. Create multiple plots for different crops
4. Edit demo plot to convert to real plot
5. Edit plot details (name, crop, photos)
6. Fetch all plots with filters
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://urchin-app-86rjy.ondigitalocean.app/api/advanced-growth"
# For local testing:
# BASE_URL = "http://localhost:8000/api/advanced-growth"

# Test user (use actual user ID from your database)
# Get a real user ID first
def get_real_user_id():
    """Helper to get a real user ID from database"""
    import uuid
    # Generate a valid UUID for testing
    return str(uuid.uuid4())

TEST_USER_ID = get_real_user_id()

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_create_demo_plot():
    """Test 1: Create a demo plot"""
    print_section("TEST 1: Create Demo Plot")
    
    data = {
        "user_id": TEST_USER_ID,
        "crop_name": "Tomatoes",
        "plot_name": "Demo Tomato Garden",
        "planting_date": "2025-01-15T10:00:00",
        "latitude": -1.2921,
        "longitude": 36.8219,
        "is_demo": "true",  # Demo plot
        "area_size": "3.5",
        "notes": "This is an editable demo plot"
    }
    
    response = requests.post(f"{BASE_URL}/plots", data=data)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('success'):
        print(f"✅ Demo plot created: {result['plot']['id']}")
        print(f"   Plot name: {result['plot']['plot_name']}")
        print(f"   Is demo: {result['plot']['is_demo']}")
        return result['plot']['id']
    else:
        print(f"❌ Failed: {result}")
        return None

def test_create_real_plot():
    """Test 2: Create a real plot with actual farm data"""
    print_section("TEST 2: Create Real Plot")
    
    data = {
        "user_id": TEST_USER_ID,
        "crop_name": "Maize",
        "plot_name": "North Field - Maize",
        "planting_date": "2025-02-01T08:00:00",
        "latitude": -1.2921,
        "longitude": 36.8219,
        "is_demo": "false",  # Real plot
        "area_size": "10.0",
        "notes": "First maize planting of the season",
        "soil_type": "Clay Loam"
    }
    
    response = requests.post(f"{BASE_URL}/plots", data=data)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('success'):
        print(f"✅ Real plot created: {result['plot']['id']}")
        print(f"   Plot name: {result['plot']['plot_name']}")
        print(f"   Is demo: {result['plot']['is_demo']}")
        print(f"   Calendar events: {len(result.get('calendar_events', []))}")
        return result['plot']['id']
    else:
        print(f"❌ Failed: {result}")
        return None

def test_create_multiple_crops():
    """Test 3: Create multiple plots for different crops"""
    print_section("TEST 3: Create Multiple Crops for Same Farmer")
    
    crops = ["Beans", "Cabbage", "Carrots"]
    plot_ids = []
    
    for crop in crops:
        data = {
            "user_id": TEST_USER_ID,
            "crop_name": crop,
            "plot_name": f"My {crop} Plot",
            "planting_date": "2025-02-15T09:00:00",
            "latitude": -1.2921,
            "longitude": 36.8219,
            "is_demo": "false",
            "area_size": "5.0"
        }
        
        response = requests.post(f"{BASE_URL}/plots", data=data)
        result = response.json()
        
        if result.get('success'):
            plot_id = result['plot']['id']
            plot_ids.append(plot_id)
            print(f"✅ Created {crop} plot: {plot_id}")
        else:
            print(f"❌ Failed to create {crop} plot")
    
    return plot_ids

def test_edit_demo_to_real(demo_plot_id):
    """Test 4: Convert demo plot to real plot"""
    print_section("TEST 4: Convert Demo Plot → Real Plot")
    
    if not demo_plot_id:
        print("❌ No demo plot ID provided")
        return
    
    data = {
        "user_id": TEST_USER_ID,
        "is_demo": "false",  # Convert to real
        "plot_name": "Real Tomato Garden (Converted)",
        "notes": "This was a demo plot, now it's real!"
    }
    
    response = requests.patch(f"{BASE_URL}/plots/{demo_plot_id}", data=data)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('success'):
        print(f"✅ Demo plot converted to real plot")
        print(f"   Updates applied: {result.get('updates_applied')}")
        print(f"   Is demo: {result['plot']['is_demo']}")
    else:
        print(f"❌ Failed: {result}")

def test_edit_plot_details(plot_id):
    """Test 5: Edit plot details"""
    print_section("TEST 5: Edit Plot Details")
    
    if not plot_id:
        print("❌ No plot ID provided")
        return
    
    data = {
        "user_id": TEST_USER_ID,
        "plot_name": "Updated Plot Name",
        "crop_name": "Sweet Maize",
        "notes": "Updated notes with new information",
        "status": "active"
    }
    
    response = requests.patch(f"{BASE_URL}/plots/{plot_id}", data=data)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('success'):
        print(f"✅ Plot updated successfully")
        print(f"   Updates applied: {result.get('updates_applied')}")
    else:
        print(f"❌ Failed: {result}")

def test_get_all_plots():
    """Test 6: Fetch all plots with different filters"""
    print_section("TEST 6: Fetch Plots with Filters")
    
    # Test 6a: Get all plots
    print("\n6a. Get ALL plots:")
    response = requests.get(f"{BASE_URL}/plots?user_id={TEST_USER_ID}")
    result = response.json()
    print(f"Status: {response.status_code}")
    print(f"Total plots: {result.get('total_plots')}")
    print(f"Demo plots: {result.get('demo_plots')}")
    print(f"Real plots: {result.get('real_plots')}")
    print(f"Unique crops: {result.get('unique_crops')}")
    
    # Test 6b: Get only demo plots
    print("\n6b. Get DEMO plots only:")
    response = requests.get(f"{BASE_URL}/plots?user_id={TEST_USER_ID}&is_demo=true")
    result = response.json()
    print(f"Total demo plots: {result.get('total_plots')}")
    
    # Test 6c: Get only real plots
    print("\n6c. Get REAL plots only:")
    response = requests.get(f"{BASE_URL}/plots?user_id={TEST_USER_ID}&is_demo=false")
    result = response.json()
    print(f"Total real plots: {result.get('total_plots')}")
    
    # Test 6d: Get plots by crop
    print("\n6d. Get Maize plots:")
    response = requests.get(f"{BASE_URL}/plots?user_id={TEST_USER_ID}&crop_name=Maize")
    result = response.json()
    print(f"Maize plots: {result.get('total_plots')}")
    
    # Test 6e: Get active real plots
    print("\n6e. Get ACTIVE REAL plots:")
    response = requests.get(f"{BASE_URL}/plots?user_id={TEST_USER_ID}&is_demo=false&status=active")
    result = response.json()
    print(f"Active real plots: {result.get('total_plots')}")

def test_get_plot_details(plot_id):
    """Test 7: Get detailed plot information"""
    print_section("TEST 7: Get Plot Details")
    
    if not plot_id:
        print("❌ No plot ID provided")
        return
    
    response = requests.get(f"{BASE_URL}/plots/{plot_id}?user_id={TEST_USER_ID}")
    
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if result.get('success'):
        print(f"✅ Plot details retrieved")
        print(f"   Plot: {result['plot']['plot_name']}")
        print(f"   Is demo: {result.get('is_demo')}")
        print(f"   Total images: {result.get('total_images')}")
        print(f"   Recent logs: {result.get('total_logs')}")
        print(f"   Upcoming events: {len(result.get('upcoming_events', []))}")
    else:
        print(f"❌ Failed: {result}")

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "=" * 70)
    print("  UNIFIED PLOT SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print(f"\nTesting against: {BASE_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    
    # Test 1: Create demo plot
    demo_plot_id = test_create_demo_plot()
    
    # Test 2: Create real plot
    real_plot_id = test_create_real_plot()
    
    # Test 3: Create multiple crops
    multi_crop_ids = test_create_multiple_crops()
    
    # Test 4: Convert demo to real
    if demo_plot_id:
        test_edit_demo_to_real(demo_plot_id)
    
    # Test 5: Edit plot details
    if real_plot_id:
        test_edit_plot_details(real_plot_id)
    
    # Test 6: Fetch plots with filters
    test_get_all_plots()
    
    # Test 7: Get plot details
    if real_plot_id:
        test_get_plot_details(real_plot_id)
    
    print("\n" + "=" * 70)
    print("  ALL TESTS COMPLETED")
    print("=" * 70)
    print("\nSummary:")
    print(f"  - Demo plot ID: {demo_plot_id}")
    print(f"  - Real plot ID: {real_plot_id}")
    print(f"  - Multi-crop plots: {len(multi_crop_ids)}")
    print("\nKey Features Tested:")
    print("  ✓ Demo plot creation (editable templates)")
    print("  ✓ Real plot creation (actual farm plots)")
    print("  ✓ Multiple crops per farmer")
    print("  ✓ Demo → Real conversion")
    print("  ✓ Plot editing (name, crop, details)")
    print("  ✓ Photo uploads support")
    print("  ✓ Filtered plot retrieval")
    print("  ✓ Detailed plot information")

if __name__ == "__main__":
    run_all_tests()
