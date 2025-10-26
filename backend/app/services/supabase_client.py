"""
Supabase Client Module
Provides a unified way to access the Supabase client
"""

from app.services.supabase_auth import supabase_client

def get_supabase_client():
    """
    Get the Supabase client instance
    
    Returns:
        Supabase client for database operations
    """
    return supabase_client
