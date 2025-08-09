# servicetitan_pyapi/auth.py
"""
ServiceTitan API Authentication Module
Single Responsibility: Handle OAuth2 authentication for ServiceTitan API
"""

import json
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import requests


@dataclass
class ServiceTitanConfig:
    """Configuration for ServiceTitan API connection"""
    client_id: str
    client_secret: str
    app_key: str
    tenant_id: str
    base_url: str = "https://api.servicetitan.io"
    _comment: Optional[str] = None  # For documentation purposes only
    
    @classmethod
    def from_file(cls, config_path: str = "servicetitan_config.json") -> 'ServiceTitanConfig':
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            data = json.load(f)
        return cls(**data)


class ServiceTitanAuth:
    """Handles OAuth2 authentication for ServiceTitan API"""
    
    def __init__(self, config: ServiceTitanConfig):
        self.config = config
        self._token: Optional[str] = None
        self._token_expires_at: float = 0
    
    @property
    def token(self) -> str:
        """Get valid access token, refreshing if necessary"""
        if self._is_token_expired():
            self._refresh_token()
        return  self._token if self._token else ""
    
    @property
    def headers(self) -> dict:
        """Get headers with valid authentication for API requests"""
        return {
            "Authorization": f"Bearer {self.token}",
            "ST-App-Key": self.config.app_key,
            "Content-Type": "application/json"
        }
    
    def _is_token_expired(self) -> bool:
        """Check if current token is expired or missing"""
        return not self._token or time.time() >= self._token_expires_at
    
    def _refresh_token(self) -> None:
        """Get new access token from ServiceTitan"""
        token_url = "https://auth.servicetitan.io/connect/token"
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self._token = token_data["access_token"]
        # Set expiration with 5-minute buffer
        self._token_expires_at = time.time() + token_data.get("expires_in", 3600) - 300


# Example servicetitan_config.json structure:
"""
{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "app_key": "your_app_key",
    "tenant_id": "your_tenant_id",
    "_comment": "Production credentials for Main Account"
}
"""

# Example usage:
"""
from servicetitan_api.auth import ServiceTitanConfig, ServiceTitanAuth
import requests

# Load config and create auth handler
config = ServiceTitanConfig.from_file("servicetitan_config.json")
auth = ServiceTitanAuth(config)

# Use auth.headers in your API calls
response = requests.get(
    f"{config.base_url}/crm/v2/tenant/{config.tenant_id}/customers",
    headers=auth.headers
)
"""