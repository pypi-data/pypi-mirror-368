# servicetitan_pyapi/clients/estimates.py
"""
ServiceTitan Estimates API
Single Responsibility: Handle estimate-related API calls
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
from ..base import BaseClient, ExportResponse


class EstimatesClient(BaseClient):
    """Client for ServiceTitan Estimates endpoints"""
    
    # Export endpoint methods
    def get_all(self) -> ExportResponse:
        """
        Retrieve all estimates from ServiceTitan (from the beginning)
        
        Returns:
            ExportResponse with all estimate data and final continuation token
        """
        # Estimates are under sales/v2 with /estimates/export path
        endpoint = f"{self.config.base_url}/sales/v2/tenant/{self.config.tenant_id}/estimates/export"
        return self._get_all_pages_custom(endpoint)
    
    def get_batch(self,
                  continuation_token: Optional[str] = None,
                  include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve a single batch of estimates
        
        Args:
            continuation_token: Token from previous export's continuation_token
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with batch data and continuation token for next call
        """
        endpoint = f"{self.config.base_url}/sales/v2/tenant/{self.config.tenant_id}/export/estimates"
        return self._get_batch_custom(endpoint, continuation_token, include_recent_changes)
    
    def get_incremental(self,
                       continuation_token: Optional[str] = None,
                       include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve all estimates from a continuation point
        
        Args:
            continuation_token: Token from previous export to continue from
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with all data from continuation point and final token
        """
        endpoint = f"{self.config.base_url}/sales/v2/tenant/{self.config.tenant_id}/estimates/export"
        return self._get_all_pages_custom(endpoint, continuation_token, include_recent_changes)
    
    def get_test(self) -> ExportResponse:
        """
        Retrieve single batch of estimates for testing
        
        Returns:
            ExportResponse with test data
        """
        endpoint = f"{self.config.base_url}/sales/v2/tenant/{self.config.tenant_id}/export/estimates"
        return self._get_batch_custom(endpoint)

    # Additional transactional endpoints for estimate details
    def get_estimate_by_id(self, estimate_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific estimate
        
        Args:
            estimate_id: The ID of the estimate
        
        Returns:
            Detailed estimate information
        """
        url = f"{self.config.base_url}/sales/v2/tenant/{self.config.tenant_id}/estimates/{estimate_id}"
        response = requests.get(url, headers=self.auth.headers)
        response.raise_for_status()
        return response.json()

