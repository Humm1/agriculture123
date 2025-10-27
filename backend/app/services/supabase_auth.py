"""
Supabase Authentication Service
Handles user authentication, registration, and session management
"""

import os
from typing import Optional, Dict
from supabase import create_client, Client
from datetime import datetime
import jwt

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "your-anon-key")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "your-service-key")

# Initialize Supabase clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Export supabase client for other modules
supabase_client = supabase


# ============================================================================
# USER REGISTRATION
# ============================================================================

async def register_user(email: str, password: str, user_type: str, metadata: Dict = None) -> Dict:
    """
    Register a new user with Supabase Auth
    
    Args:
        email: User's email address
        password: User's password
        user_type: "farmer" or "buyer"
        metadata: Additional user data (name, phone, etc.)
    
    Returns:
        User data and session info
    """
    try:
        # Create user in Supabase Auth
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "user_type": user_type,
                    **(metadata or {})
                }
            }
        })
        
        if response.user:
            # Create user profile in database
            user_profile = {
                "user_id": response.user.id,
                "email": email,
                "user_type": user_type,
                "created_at": datetime.now().isoformat(),
                "email_confirmed": False,
                **(metadata or {})
            }
            
            # Insert into profiles table
            supabase.table("profiles").insert(user_profile).execute()
            
            return {
                "status": "success",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_type": user_type,
                    "email_confirmed": response.user.email_confirmed_at is not None
                },
                "session": {
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None,
                    "expires_at": response.session.expires_at if response.session else None
                },
                "message": "Registration successful. Please check your email to verify your account."
            }
        else:
            return {
                "status": "error",
                "message": "Registration failed. Please try again."
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================================
# USER LOGIN
# ============================================================================

async def login_user(email: str, password: str) -> Dict:
    """
    Authenticate user and create session
    
    Args:
        email: User's email
        password: User's password
    
    Returns:
        User data and session tokens
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user and response.session:
            # Get user profile
            profile = supabase.table("profiles").select("*").eq("user_id", response.user.id).single().execute()
            
            return {
                "status": "success",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_type": profile.data.get("user_type") if profile.data else None,
                    "profile": profile.data if profile.data else {}
                },
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at,
                    "token_type": response.session.token_type
                }
            }
        else:
            return {
                "status": "error",
                "message": "Invalid email or password"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================================
# TOKEN VERIFICATION
# ============================================================================

async def verify_token(token: str) -> Optional[Dict]:
    """
    Verify JWT token and return user data
    
    Args:
        token: JWT access token
    
    Returns:
        User data if valid, None if invalid
    """
    try:
        response = supabase.auth.get_user(token)
        
        if response.user:
            # Get user profile
            profile = supabase.table("profiles").select("*").eq("user_id", response.user.id).single().execute()
            
            return {
                "user_id": response.user.id,
                "email": response.user.email,
                "user_type": profile.data.get("user_type") if profile.data else None,
                "profile": profile.data if profile.data else {}
            }
        
        return None
    
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return None


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

async def refresh_session(refresh_token: str) -> Dict:
    """
    Refresh access token using refresh token
    
    Args:
        refresh_token: Refresh token
    
    Returns:
        New session tokens
    """
    try:
        response = supabase.auth.refresh_session(refresh_token)
        
        if response.session:
            return {
                "status": "success",
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at
                }
            }
        else:
            return {
                "status": "error",
                "message": "Failed to refresh session"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


async def logout_user(token: str) -> Dict:
    """
    Sign out user and invalidate session
    
    Args:
        token: Access token (optional - if provided, will use admin client)
    
    Returns:
        Logout status
    """
    try:
        # Sign out from Supabase
        # This will invalidate the session on the server side
        supabase.auth.sign_out()
        
        # If token is provided, we could optionally revoke it server-side
        # Note: Supabase automatically handles session invalidation
        
        return {
            "status": "success",
            "message": "Logged out successfully"
        }
    
    except Exception as e:
        # Even if there's an error, we should still clear client-side session
        return {
            "status": "success",  # Return success to allow client-side cleanup
            "message": "Logged out (with warning)",
            "warning": str(e)
        }


# ============================================================================
# PASSWORD MANAGEMENT
# ============================================================================

async def reset_password_request(email: str) -> Dict:
    """
    Send password reset email
    
    Args:
        email: User's email address
    
    Returns:
        Reset request status
    """
    try:
        supabase.auth.reset_password_email(email)
        
        return {
            "status": "success",
            "message": "Password reset email sent. Please check your inbox."
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


async def update_password(token: str, new_password: str) -> Dict:
    """
    Update user password
    
    Args:
        token: Access token
        new_password: New password
    
    Returns:
        Update status
    """
    try:
        response = supabase.auth.update_user({
            "password": new_password
        })
        
        if response.user:
            return {
                "status": "success",
                "message": "Password updated successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to update password"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================================
# USER PROFILE
# ============================================================================

async def get_user_profile(user_id: str) -> Optional[Dict]:
    """
    Get user profile from database
    
    Args:
        user_id: User's unique ID
    
    Returns:
        User profile data
    """
    try:
        response = supabase.table("profiles").select("*").eq("user_id", user_id).single().execute()
        return response.data if response.data else None
    
    except Exception as e:
        print(f"Error fetching profile: {str(e)}")
        return None


async def update_user_profile(user_id: str, profile_data: Dict) -> Dict:
    """
    Update user profile
    
    Args:
        user_id: User's unique ID
        profile_data: Profile fields to update
    
    Returns:
        Update status
    """
    try:
        profile_data["updated_at"] = datetime.now().isoformat()
        
        response = supabase.table("profiles").update(profile_data).eq("user_id", user_id).execute()
        
        if response.data:
            return {
                "status": "success",
                "profile": response.data[0] if response.data else {}
            }
        else:
            return {
                "status": "error",
                "message": "Failed to update profile"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================================
# ADMIN FUNCTIONS
# ============================================================================

async def get_all_users(user_type: Optional[str] = None, limit: int = 100) -> Dict:
    """
    Get all users (admin only)
    
    Args:
        user_type: Filter by user type
        limit: Maximum number of users to return
    
    Returns:
        List of users
    """
    try:
        query = supabase_admin.table("profiles").select("*")
        
        if user_type:
            query = query.eq("user_type", user_type)
        
        response = query.limit(limit).execute()
        
        return {
            "status": "success",
            "users": response.data if response.data else [],
            "count": len(response.data) if response.data else 0
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


async def delete_user(user_id: str) -> Dict:
    """
    Delete user account (admin only)
    
    Args:
        user_id: User ID to delete
    
    Returns:
        Deletion status
    """
    try:
        # Delete from auth
        supabase_admin.auth.admin.delete_user(user_id)
        
        # Delete profile
        supabase.table("profiles").delete().eq("user_id", user_id).execute()
        
        return {
            "status": "success",
            "message": "User deleted successfully"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def extract_user_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from JWT token without verification
    (Use verify_token for secure verification)
    
    Args:
        token: JWT token
    
    Returns:
        User ID if found
    """
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded.get("sub")
    
    except Exception as e:
        print(f"Token decode error: {str(e)}")
        return None
