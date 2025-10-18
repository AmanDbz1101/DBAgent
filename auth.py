"""
Authentication module for the Inventory Management System.
Handles user authentication using Supabase Auth.
"""

import os
import streamlit as st
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

class AuthManager:
    """Manages user authentication with Supabase."""
    
    def __init__(self):
        """Initialize the AuthManager with Supabase client."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and Key must be provided in environment variables")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def sign_in(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Sign in a user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (success, message, user_data)
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return True, "Successfully signed in!", {
                    "id": response.user.id,
                    "email": response.user.email,
                    "access_token": response.session.access_token if response.session else None
                }
            else:
                return False, "Invalid email or password", None
                
        except Exception as e:
            error_msg = str(e)
            if "Invalid login credentials" in error_msg:
                return False, "Invalid email or password", None
            elif "Email not confirmed" in error_msg:
                return False, "Please check your email and confirm your account", None
            else:
                return False, f"Authentication error: {error_msg}", None
    
    def sign_out(self) -> Tuple[bool, str]:
        """
        Sign out the current user.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            self.supabase.auth.sign_out()
            return True, "Successfully signed out"
        except Exception as e:
            return False, f"Error signing out: {str(e)}"
    
    def get_current_user(self) -> Optional[Dict]:
        """
        Get the current authenticated user.
        
        Returns:
            User data dictionary or None if not authenticated
        """
        try:
            user = self.supabase.auth.get_user()
            if user and user.user:
                return {
                    "id": user.user.id,
                    "email": user.user.email
                }
            return None
        except Exception:
            return None
    
    def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        return self.get_current_user() is not None

def initialize_auth_session():
    """Initialize authentication-related session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "user_data" not in st.session_state:
        st.session_state.user_data = None
    
    if "auth_manager" not in st.session_state:
        try:
            st.session_state.auth_manager = AuthManager()
        except ValueError as e:
            st.error(f"Configuration Error: {str(e)}")
            st.stop()

def check_authentication() -> bool:
    """
    Check if the user is authenticated.
    
    Returns:
        True if authenticated, False otherwise
    """
    initialize_auth_session()
    return st.session_state.authenticated

def login_user(email: str, password: str) -> Tuple[bool, str]:
    """
    Login a user and update session state.
    
    Args:
        email: User's email
        password: User's password
        
    Returns:
        Tuple of (success, message)
    """
    initialize_auth_session()
    
    success, message, user_data = st.session_state.auth_manager.sign_in(email, password)
    
    if success and user_data:
        st.session_state.authenticated = True
        st.session_state.user_data = user_data
        return True, message
    else:
        st.session_state.authenticated = False
        st.session_state.user_data = None
        return False, message

def login_as_guest() -> Tuple[bool, str]:
    """
    Login as a guest user with access to Guest table.
    
    Returns:
        Tuple of (success, message)
    """
    initialize_auth_session()
    
    # Set guest session data
    st.session_state.authenticated = True
    st.session_state.user_data = {
        "id": "guest",
        "email": "guest@demo.local",
        "is_guest": True
    }
    
    return True, "Signed in as Guest user"

def logout_user() -> Tuple[bool, str]:
    """
    Logout the current user and clear session state.
    
    Returns:
        Tuple of (success, message)
    """
    if "auth_manager" in st.session_state and not is_guest_user():
        success, message = st.session_state.auth_manager.sign_out()
    else:
        success, message = True, "Logged out"
    
    # Clear session state
    st.session_state.authenticated = False
    st.session_state.user_data = None
    
    # Clear other session state related to the app
    if "messages" in st.session_state:
        del st.session_state.messages
    if "workflow" in st.session_state:
        del st.session_state.workflow
    
    return success, message

def is_guest_user() -> bool:
    """
    Check if the current user is a guest user.
    
    Returns:
        True if current user is guest, False otherwise
    """
    user = get_current_user()
    if user:
        return user.get("is_guest", False)
    return False

def get_user_table_name() -> str:
    """
    Get the appropriate table name based on user type.
    
    Returns:
        Table name string ("Guest" for guest users, "Inventory" for authenticated users)
    """
    if is_guest_user():
        return "Guest"
    else:
        return "Inventory"

def get_current_user() -> Optional[Dict]:
    """
    Get the current authenticated user data.
    
    Returns:
        User data dictionary or None
    """
    if check_authentication():
        return st.session_state.user_data
    return None