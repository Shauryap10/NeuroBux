import streamlit as st
from supabase import Client
import re
import hashlib

class AuthManager:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    def is_valid_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def is_valid_password(self, password):
        """Validate password strength"""
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        if not re.search(r'[A-Za-z]', password):
            return False, "Password must contain at least one letter"
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        return True, "Valid password"
    
    def register(self, email, password, confirm_password):
        """Register a new user with validation"""
        try:
            # Validate inputs
            if not email or not password:
                return False, "Email and password are required"
            
            if not self.is_valid_email(email):
                return False, "Please enter a valid email address"
            
            if password != confirm_password:
                return False, "Passwords do not match"
            
            is_valid, message = self.is_valid_password(password)
            if not is_valid:
                return False, message
            
            # Check if user already exists
            existing_user = self.supabase.table("auth_users").select("email").eq("email", email.lower().strip()).execute()
            if existing_user.data:
                return False, "An account with this email already exists"
            
            # Create user in our custom auth table
            user_data = {
                "email": email.lower().strip(),
                "password_hash": self._hash_password(password),
                "is_verified": False
            }
            
            result = self.supabase.table("auth_users").insert(user_data).execute()
            
            return True, "Account created successfully! Please login with your credentials."
            
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login(self, email, password):
        """Login user with proper validation"""
        try:
            if not email or not password:
                return False, "Email and password are required"
            
            if not self.is_valid_email(email):
                return False, "Please enter a valid email address"
            
            # Get user from database
            user_result = self.supabase.table("auth_users").select("*").eq("email", email.lower().strip()).execute()
            
            if not user_result.data:
                return False, "Invalid email or password"
            
            user = user_result.data[0]
            
            # Verify password
            if not self._verify_password(password, user["password_hash"]):
                return False, "Invalid email or password"
            
            # Update last login
            self.supabase.table("auth_users").update({"last_login": "now()"}).eq("email", email.lower().strip()).execute()
            
            return True, "Login successful!"
            
        except Exception as e:
            return False, f"Login failed: {str(e)}"
    
    def _hash_password(self, password):
        """Simple password hashing (use proper hashing in production)"""
        salt = "neurobux_salt_2025"  # In production, use random salt per user
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _verify_password(self, password, password_hash):
        """Verify password against hash"""
        return self._hash_password(password) == password_hash
    
    def change_password(self, email, old_password, new_password):
        """Change user password"""
        try:
            # Verify current password first
            user_result = self.supabase.table("auth_users").select("*").eq("email", email.lower().strip()).execute()
            
            if not user_result.data:
                return False, "User not found"
            
            user = user_result.data[0]
            
            if not self._verify_password(old_password, user["password_hash"]):
                return False, "Current password is incorrect"
            
            # Validate new password
            is_valid, message = self.is_valid_password(new_password)
            if not is_valid:
                return False, message
            
            # Update password
            new_hash = self._hash_password(new_password)
            self.supabase.table("auth_users").update({"password_hash": new_hash}).eq("email", email.lower().strip()).execute()
            
            return True, "Password changed successfully!"
            
        except Exception as e:
            return False, f"Password change failed: {str(e)}"
    
    def get_user_info(self, email):
        """Get user information - THIS WAS THE MISSING METHOD"""
        try:
            user_result = self.supabase.table("auth_users").select("email, created_at, last_login, is_verified").eq("email", email.lower().strip()).execute()
            
            if user_result.data:
                return user_result.data[0]
            return None
            
        except Exception as e:
            st.error(f"Error fetching user info: {str(e)}")
            return None
