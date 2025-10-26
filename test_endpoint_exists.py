"""Quick test to check if unified plot endpoints exist on server"""
import requests

BASE_URL = "https://urchin-app-86rjy.ondigitalocean.app/api/advanced-growth"

def test_endpoint_exists():
    """Test if POST /plots endpoint exists"""
    try:
        # Try OPTIONS request to see if endpoint exists
        response = requests.options(f"{BASE_URL}/plots")
        print(f"OPTIONS /plots: {response.status_code}")
        print(f"Allowed methods: {response.headers.get('Allow', 'Not specified')}")
        
        # Try GET to the endpoint (should work even without auth)
        response2 = requests.get(f"{BASE_URL}/plots?user_id=test")
        print(f"\nGET /plots: {response2.status_code}")
        print(f"Response: {response2.text[:200]}")
        
        # Check root endpoint
        response3 = requests.get("https://urchin-app-86rjy.ondigitalocean.app")
        print(f"\nRoot endpoint: {response3.status_code}")
        print(f"Response: {response3.text[:200]}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoint_exists()
