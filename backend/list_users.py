"""
List all users in the database
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.supabase_auth import supabase_client

def list_users():
    """List all users from profiles table"""
    try:
        print("📋 Fetching users from database...\n")
        
        # Try profiles table first
        result = supabase_client.table('profiles').select('id, email, full_name, role').execute()
        
        if result.data:
            print(f"Found {len(result.data)} users:\n")
            for i, user in enumerate(result.data, 1):
                print(f"{i}. ID: {user.get('id')}")
                print(f"   Email: {user.get('email', 'N/A')}")
                print(f"   Name: {user.get('full_name', 'N/A')}")
                print(f"   Role: {user.get('role', 'N/A')}")
                print()
            
            # Show the first user ID for easy copying
            if len(result.data) > 0:
                first_user_id = result.data[0].get('id')
                print(f"💡 To seed data for the first user, run:")
                print(f"   python seed_growth_data.py {first_user_id}")
        else:
            print("❌ No users found in profiles table")
            print("   Make sure you have created a user account in your app")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_users()
