# servicetitan_pyapi/base.py
"""
Base client for ServiceTitan API calls
Single Responsibility: Handle common API request logic
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import requests
from .auth import ServiceTitanAuth, ServiceTitanConfig


@dataclass
class ExportResponse:
    """Response from ServiceTitan export endpoints"""
    data: List[Dict[str, Any]]
    continuation_token: Optional[str] = None
    has_more: bool = False
    
    def __len__(self) -> int:
        """Return count of records in this response"""
        return len(self.data)


class BaseClient:
    """Base client for all ServiceTitan API interactions"""
    
    def __init__(self, auth: ServiceTitanAuth):
        self.auth = auth
        self.config = auth.config
        self.base_url = f"{self.config.base_url}/crm/v2/tenant/{self.config.tenant_id}"
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request to ServiceTitan API"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.auth.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def _get_batch(self, 
                   endpoint: str, 
                   continuation_token: Optional[str] = None,
                   include_recent_changes: bool = False) -> ExportResponse:
        """
        Get a single batch of results with continuation token
        
        Returns:
            ExportResponse with data and continuation token for next call
        """
        params = {}
        
        if continuation_token:
            params['from'] = continuation_token
        
        if include_recent_changes:
            params['includeRecentChanges'] = 'true'
        
        response = self._get(endpoint, params)
        
        return ExportResponse(
            data=response.get('data', []),
            continuation_token=response.get('continueFrom', None),
            has_more=bool(response.get('continueFrom', None))
        )
    
    def _get_all_pages(self, 
                       endpoint: str, 
                       continuation_token: Optional[str] = None,
                       include_recent_changes: bool = False) -> ExportResponse:
        """
        Get all pages of results from paginated endpoint
        
        Returns:
            ExportResponse with all data and final continuation token
        """
        all_data = []
        current_token = continuation_token
        
        while True:
            batch = self._get_batch(endpoint, current_token, include_recent_changes)
            all_data.extend(batch.data)
            
            if not batch.has_more:
                # Return accumulated data with the last token for future runs
                return ExportResponse(
                    data=all_data,
                    continuation_token=batch.continuation_token,
                    has_more=False
                )
            
            current_token = batch.continuation_token
    
    def _get_batch_custom(self, 
                         endpoint: str,
                         continuation_token: Optional[str] = None,
                         include_recent_changes: bool = False) -> ExportResponse:
        """Get a single batch from a custom endpoint with full URL"""
        params = {}
        
        if continuation_token:
            params['from'] = continuation_token
        
        if include_recent_changes:
            params['includeRecentChanges'] = 'true'
        
        response = requests.get(endpoint, headers=self.auth.headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        return ExportResponse(
            data=data.get('data', []),
            continuation_token=data.get('continueFrom', None),
            has_more=bool(data.get('continueFrom', None))
        )
    
    def _get_all_pages_custom(self,
                             endpoint: str,
                             continuation_token: Optional[str] = None,
                             include_recent_changes: bool = False) -> ExportResponse:
        """Get all pages from a custom endpoint with full URL"""
        all_data = []
        current_token = continuation_token
        
        while True:
            batch = self._get_batch_custom(endpoint, current_token, include_recent_changes)
            all_data.extend(batch.data)
            
            if not batch.has_more:
                return ExportResponse(
                    data=all_data,
                    continuation_token=batch.continuation_token,
                    has_more=False
                )
            
            current_token = batch.continuation_token
