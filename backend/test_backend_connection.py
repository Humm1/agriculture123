"""
Quick test script to check if backend is responding
"""
import requests
import sys

def test_backend():
    print("🧪 Testing backend connectivity...")
    
    base_url = "https://urchin-app-86rjy.ondigitalocean.app"
    
    # Test 1: Health check
    try:
        print(f"\n1️⃣  Testing health endpoint: {base_url}/api/advanced-growth/health")
        response = requests.get(f"{base_url}/api/advanced-growth/health", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Backend is running! Response: {response.json()}")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except requests.exceptions.Timeout:
        print("   ⏱️  Timeout - backend not responding")
        print("\n💡 Solution: Check DigitalOcean deployment status")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection refused - backend is not running")
        print("\n💡 Solution: Check DigitalOcean deployment status")
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        sys.exit(1)
    
    # Test 2: Plots endpoint
    user_id = "8b7617ea-2437-402b-81f9-56f88ef2f8c8"
    try:
        print(f"\n2️⃣  Testing plots endpoint: {base_url}/api/advanced-growth/plots/user/{user_id}")
        response = requests.get(f"{base_url}/api/advanced-growth/plots/user/{user_id}", timeout=3)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {data}")
        
        if data.get('success'):
            plot_count = len(data.get('plots', []))
            print(f"   ✅ Found {plot_count} plots")
        else:
            print(f"   ⚠️  No plots found for user")
    except requests.exceptions.Timeout:
        print("   ⏱️  Timeout - endpoint is hanging")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ Backend test complete!")

if __name__ == "__main__":
    test_backend()
