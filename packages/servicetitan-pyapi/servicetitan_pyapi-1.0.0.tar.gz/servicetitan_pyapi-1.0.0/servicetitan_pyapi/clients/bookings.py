# servicetitan_pyapi/clients/bookings.py
"""
ServiceTitan Bookings API
Single Responsibility: Handle booking-related API calls
"""

from typing import Optional
from ..base import BaseClient, ExportResponse


class BookingsClient(BaseClient):
    """Client for ServiceTitan Bookings endpoints"""
    
    def get_all(self) -> ExportResponse:
        """Retrieve all bookings from ServiceTitan (from the beginning)"""
        return self._get_all_pages('export/bookings')
    
    def get_batch(self,
                  continuation_token: Optional[str] = None,
                  include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve a single batch of bookings
        
        Args:
            continuation_token: Token from previous export's continuation_token
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with batch data and continuation token for next call
        """
        return self._get_batch('export/bookings', continuation_token, include_recent_changes)
    
    def get_incremental(self,
                       continuation_token: Optional[str] = None,
                       include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve all bookings from a continuation point
        
        Args:
            continuation_token: Token from previous export to continue from
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with all data from continuation point and final token
        """
        return self._get_all_pages('export/bookings', continuation_token, include_recent_changes)
    
    def get_test(self) -> ExportResponse:
        """Retrieve single batch of bookings for testing"""
        return self._get_batch('export/bookings')

