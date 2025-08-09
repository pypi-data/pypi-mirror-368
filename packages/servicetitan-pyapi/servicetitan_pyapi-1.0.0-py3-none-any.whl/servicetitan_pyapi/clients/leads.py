# servicetitan_pyapi/clients/leads.py
"""
ServiceTitan Leads API
Single Responsibility: Handle lead-related API calls
"""

from typing import Optional
from ..base import BaseClient, ExportResponse


class LeadsClient(BaseClient):
    """Client for ServiceTitan Leads endpoints"""
    
    def get_all(self) -> ExportResponse:
        """Retrieve all leads from ServiceTitan (from the beginning)"""
        return self._get_all_pages('export/leads')
    
    def get_batch(self,
                  continuation_token: Optional[str] = None,
                  include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve a single batch of leads
        
        Args:
            continuation_token: Token from previous export's continuation_token
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with batch data and continuation token for next call
        """
        return self._get_batch('export/leads', continuation_token, include_recent_changes)
    
    def get_incremental(self,
                       continuation_token: Optional[str] = None,
                       include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve all leads from a continuation point
        
        Args:
            continuation_token: Token from previous export to continue from
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with all data from continuation point and final token
        """
        return self._get_all_pages('export/leads', continuation_token, include_recent_changes)
    
    def get_test(self) -> ExportResponse:
        """Retrieve single batch of leads for testing"""
        return self._get_batch('export/leads')
