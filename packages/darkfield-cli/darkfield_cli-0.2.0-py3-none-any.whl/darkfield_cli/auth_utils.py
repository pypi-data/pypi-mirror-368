"""Authentication utilities for darkfield CLI"""

import keyring
from typing import Optional, Dict

def get_current_user() -> Optional[Dict[str, str]]:
    """Get current authenticated user info"""
    try:
        email = keyring.get_password("darkfield-cli", "user_email")
        user_id = keyring.get_password("darkfield-cli", "user_id")
        api_key = keyring.get_password("darkfield-cli", "api_key")
        
        if email and user_id and api_key:
            return {
                "email": email,
                "user_id": user_id,
                "api_key": api_key,
                "tier": "pay_as_you_go",  # Would be fetched from API
                "organization": "Personal"  # Would be fetched from API
            }
    except Exception:
        pass
    
    return None