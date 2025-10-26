"""
Test if the backend endpoints are accessible
"""
import requests
import json

BASE_URL = "https://urchin-app-86rjy.ondigitalocean.app"

print("Testing Backend Endpoints")
print("=" * 60)

# Test 1: Root endpoint
print("\n1. Testing root endpoint...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Root endpoint working")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Advanced growth test endpoint
print("\n2. Testing /api/advanced-growth/test...")
try:
    response = requests.get(f"{BASE_URL}/api/advanced-growth/test", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Test endpoint working")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ❌ Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Create plot endpoint (should return 422 without data)
print("\n3. Testing /api/advanced-growth/plots/create-manual...")
try:
    response = requests.post(
        f"{BASE_URL}/api/advanced-growth/plots/create-manual",
        data={},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print(f"   ✅ Endpoint exists (422 = validation error, expected)")
    elif response.status_code == 404:
        print(f"   ❌ Endpoint not found - backend not deployed yet")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Get user plots endpoint
print("\n4. Testing /api/advanced-growth/plots/user/test-user...")
try:
    response = requests.get(
        f"{BASE_URL}/api/advanced-growth/plots/user/test-user",
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 500]:
        print(f"   ✅ Endpoint exists")
        print(f"   Response: {response.text[:200]}")
    elif response.status_code == 404:
        print(f"   ❌ Endpoint not found")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("Testing complete!")
