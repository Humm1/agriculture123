"""
Quick test to verify backend is accessible and endpoint exists
"""
import requests

BASE_URL = "https://urchin-app-86rjy.ondigitalocean.app"

print("Testing backend connection...")
print("=" * 60)

# Test 1: Check if backend is alive
try:
    response = requests.get(f"{BASE_URL}/", timeout=10)
    print(f"✅ Backend is alive - Status: {response.status_code}")
except Exception as e:
    print(f"❌ Backend not accessible: {e}")

# Test 2: Check if the endpoint exists
try:
    response = requests.post(
        f"{BASE_URL}/api/advanced-growth/plots/create-manual",
        data={"test": "test"},
        timeout=10
    )
    print(f"✅ Endpoint exists - Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Endpoint error: {e}")

print("=" * 60)
