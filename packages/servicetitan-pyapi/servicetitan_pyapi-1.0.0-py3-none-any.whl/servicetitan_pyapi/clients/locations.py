# servicetitan_pyapi/clients/locations.py
"""
ServiceTitan Locations API
Single Responsibility: Handle location-related API calls
"""

from typing import Optional
from ..base import BaseClient, ExportResponse


class LocationsClient(BaseClient):
    """Client for ServiceTitan Locations endpoints"""
    
    def get_all(self) -> ExportResponse:
        """Retrieve all locations from ServiceTitan (from the beginning)"""
        return self._get_all_pages('export/locations')
    
    def get_batch(self,
                  continuation_token: Optional[str] = None,
                  include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve a single batch of locations
        
        Args:
            continuation_token: Token from previous export's continuation_token
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with batch data and continuation token for next call
        """
        return self._get_batch('export/locations', continuation_token, include_recent_changes)
    
    def get_incremental(self,
                       continuation_token: Optional[str] = None,
                       include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve all locations from a continuation point
        
        Args:
            continuation_token: Token from previous export to continue from
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with all data from continuation point and final token
        """
        return self._get_all_pages('export/locations', continuation_token, include_recent_changes)
    
    def get_test(self) -> ExportResponse:
        """Retrieve single batch of locations for testing"""
        return self._get_batch('export/locations')
    
    # Location Contacts methods
    def get_all_contacts(self) -> ExportResponse:
        """Retrieve all location contacts from ServiceTitan"""
        return self._get_all_pages('export/locations/contacts')
    
    def get_contacts_batch(self,
                          continuation_token: Optional[str] = None,
                          include_recent_changes: bool = False) -> ExportResponse:
        """Retrieve a single batch of location contacts"""
        return self._get_batch('export/locations/contacts', continuation_token, include_recent_changes)
    
    def get_contacts_incremental(self,
                                continuation_token: Optional[str] = None,
                                include_recent_changes: bool = False) -> ExportResponse:
        """Retrieve all location contacts from a continuation point"""
        return self._get_all_pages('export/locations/contacts', continuation_token, include_recent_changes)
    
    def get_test_contacts(self) -> ExportResponse:
        """Retrieve single batch of location contacts for testing"""
        return self._get_batch('export/locations/contacts')
