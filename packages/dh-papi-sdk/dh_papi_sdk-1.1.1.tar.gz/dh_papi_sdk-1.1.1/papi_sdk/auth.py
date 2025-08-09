# /sdk/py/papi-sdk/papi_sdk/auth.py
"""
Simplified authentication client that works around urllib3 issues
"""

import requests
from datetime import datetime, timedelta
from typing import Optional


class AuthClient:
    """Handles authentication for the Platform API - SIMPLIFIED VERSION"""
    
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: Optional[str] = None
        self._token_expires: Optional[datetime] = None
        
        print(f"✅ AuthClient initialized for: {self.base_url}")
        
    def get_token(self, force_refresh: bool = False) -> str:
        """Get a valid access token, refreshing if necessary"""
        if force_refresh or self._is_token_expired():
            self._refresh_token()
        return self._token
    
    def _is_token_expired(self) -> bool:
        """Check if the current token is expired or will expire soon"""
        if not self._token or not self._token_expires:
            return True
        # Refresh 5 minutes before expiry
        return datetime.now() >= (self._token_expires - timedelta(minutes=5))
    
    def _refresh_token(self) -> None:
        """Get a new access token from the auth endpoint - SIMPLIFIED"""
        url = f"{self.base_url}/auth/v2/token"
        print(f"🔐 Requesting token from: {url}")
        
        # OAuth 2.0 client credentials flow - matches your Go SDK exactly
        params = {
            "grant_type": "client_credentials"
        }
        
        # Form data as x-www-form-urlencoded (matches Go SDK)
        form_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            # Use basic requests with minimal configuration to avoid urllib3 issues
            response = requests.post(
                url, 
                params=params, 
                data=form_data, 
                headers=headers,
                timeout=30,
                verify=False  # Disable SSL verification to avoid urllib3 issues
            )
            
            response.raise_for_status()
            
            data = response.json()
            self._token = data["access_token"]
            expires_in = data.get("expires_in", 3600)  # Default 1 hour
            self._token_expires = datetime.now() + timedelta(seconds=expires_in)
            
            print(f"✅ Token obtained successfully (expires in {expires_in}s)")
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if any(key in error_msg for key in ['key_ca_cert_data', 'key_check_hostname']):
                raise Exception(f"SSL/urllib3 compatibility issue: {e}")
            else:
                raise Exception(f"Authentication request failed: {e}")
        except Exception as e:
            raise Exception(f"Token refresh failed: {e}")
