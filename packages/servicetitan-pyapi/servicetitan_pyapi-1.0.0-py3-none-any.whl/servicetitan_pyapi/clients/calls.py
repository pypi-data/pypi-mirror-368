# servicetitan_pyapi/clients/calls.py
"""
ServiceTitan Calls API
Single Responsibility: Handle call-related API calls
"""

from typing import Optional, List, Dict, Any
import requests
from ..base import BaseClient, ExportResponse


class CallsClient(BaseClient):
    """Client for ServiceTitan Calls endpoints"""
    
    # Export endpoint methods (follows same pattern as other export clients)
    def get_all(self) -> ExportResponse:
        """
        Retrieve all calls from ServiceTitan (from the beginning)
        
        Returns:
            ExportResponse with all call data and final continuation token
        """
        # Calls are under telecom/v2, not crm/v2
        endpoint = f"{self.config.base_url}/telecom/v2/tenant/{self.config.tenant_id}/export/calls"
        return self._get_all_pages_custom(endpoint)
    
    def get_batch(self,
                  continuation_token: Optional[str] = None,
                  include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve a single batch of calls
        
        Args:
            continuation_token: Token from previous export's continuation_token
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with batch data and continuation token for next call
        """
        endpoint = f"{self.config.base_url}/telecom/v2/tenant/{self.config.tenant_id}/export/calls"
        return self._get_batch_custom(endpoint, continuation_token, include_recent_changes)
    
    def get_incremental(self,
                       continuation_token: Optional[str] = None,
                       include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve all calls from a continuation point
        
        Args:
            continuation_token: Token from previous export to continue from
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with all data from continuation point and final token
        """
        endpoint = f"{self.config.base_url}/telecom/v2/tenant/{self.config.tenant_id}/export/calls"
        return self._get_all_pages_custom(endpoint, continuation_token, include_recent_changes)
    
    def get_test(self) -> ExportResponse:
        """
        Retrieve single batch of calls for testing
        
        Returns:
            ExportResponse with test data
        """
        endpoint = f"{self.config.base_url}/telecom/v2/tenant/{self.config.tenant_id}/export/calls"
        return self._get_batch_custom(endpoint)
    
    # Transactional endpoint methods
    def get_call_reasons(self, 
                        active_only: bool = True,
                        page: int = 1,
                        page_size: int = 100) -> Dict[str, Any]:
        """
        Get call reasons from ServiceTitan (transactional endpoint)
        
        Args:
            active_only: If True, only return active call reasons
            page: Page number for pagination
            page_size: Number of items per page (max 100)
        
        Returns:
            Dict containing call reasons data and pagination info
        """
        params: Dict[str, Any] = {
            'page': page,
            'pageSize': min(page_size, 100)  # Cap at 100
        }
        
        if active_only:
            params['active'] = 'true'
        
        # Call reasons are under jbce/v2, not crm/v2
        url = f"{self.config.base_url}/jbce/v2/tenant/{self.config.tenant_id}/call-reasons"
        response = requests.get(url, headers=self.auth.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_all_call_reasons(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all call reasons, handling pagination automatically
        
        Args:
            active_only: If True, only return active call reasons
        
        Returns:
            List of all call reasons
        """
        all_reasons = []
        page = 1
        
        while True:
            response = self.get_call_reasons(active_only=active_only, page=page, page_size=100)
            
            data = response.get('data', [])
            all_reasons.extend(data)
            
            # Check if there are more pages
            if not response.get('hasMore', False):
                break
                
            page += 1
        
        return all_reasons
