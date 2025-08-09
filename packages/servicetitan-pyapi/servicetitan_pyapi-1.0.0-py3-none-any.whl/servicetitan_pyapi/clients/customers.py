# servicetitan_pyapi/clients/customers.py
"""
ServiceTitan Customers API
Single Responsibility: Handle customer-related API calls
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from ..base import BaseClient, ExportResponse


class CustomersClient(BaseClient):
    """Client for ServiceTitan Customers endpoints"""
    
    def get_all(self) -> ExportResponse:
        """
        Retrieve all customers from ServiceTitan (from the beginning)
        
        Returns:
            ExportResponse with all customer data and final continuation token
        """
        return self._get_all_pages('export/customers')
    
    def get_batch(self, 
                  continuation_token: Optional[str] = None,
                  include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve a single batch of customers
        
        Args:
            continuation_token: Token from previous export's continuation_token
                              Use None to start from beginning
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with batch data and continuation token for next call
        """
        return self._get_batch('export/customers', continuation_token, include_recent_changes)
    
    def get_incremental(self,
                       continuation_token: Optional[str] = None,
                       include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve all customers from a continuation point
        
        Args:
            continuation_token: Token from previous export to continue from
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with all data from continuation point and final token
        """
        return self._get_all_pages('export/customers', continuation_token, include_recent_changes)
    
    def get_test(self) -> ExportResponse:
        """
        Retrieve single batch of customers for testing
        
        Returns:
            ExportResponse with test data
        """
        return self._get_batch('export/customers')
    
    # Customer Contacts methods
    def get_all_contacts(self) -> ExportResponse:
        """Retrieve all customer contacts from ServiceTitan"""
        return self._get_all_pages('export/customers/contacts')
    
    def get_contacts_batch(self,
                          continuation_token: Optional[str] = None,
                          include_recent_changes: bool = False) -> ExportResponse:
        """Retrieve a single batch of customer contacts"""
        return self._get_batch('export/customers/contacts', continuation_token, include_recent_changes)
    
    def get_contacts_incremental(self,
                                continuation_token: Optional[str] = None,
                                include_recent_changes: bool = False) -> ExportResponse:
        """Retrieve all customer contacts from a continuation point"""
        return self._get_all_pages('export/customers/contacts', continuation_token, include_recent_changes)
    
    def get_test_contacts(self) -> ExportResponse:
        """Retrieve single batch of customer contacts for testing"""
        return self._get_batch('export/customers/contacts')

