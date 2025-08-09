# servicetitan_pyapi/clients/invoices.py
"""
ServiceTitan Invoices API
Single Responsibility: Handle invoice-related API calls for revenue tracking
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
from ..base import BaseClient, ExportResponse


class InvoicesClient(BaseClient):
    """Client for ServiceTitan Invoices endpoints"""
    
    # Export endpoint methods
    def get_all(self) -> ExportResponse:
        """
        Retrieve all invoices from ServiceTitan (from the beginning)
        
        Returns:
            ExportResponse with all invoice data and final continuation token
        """
        # Invoices are under accounting/v2
        endpoint = f"{self.config.base_url}/accounting/v2/tenant/{self.config.tenant_id}/export/invoices"
        return self._get_all_pages_custom(endpoint)
    
    def get_batch(self,
                  continuation_token: Optional[str] = None,
                  include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve a single batch of invoices
        
        Args:
            continuation_token: Token from previous export's continuation_token
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with batch data and continuation token for next call
        """
        endpoint = f"{self.config.base_url}/accounting/v2/tenant/{self.config.tenant_id}/export/invoices"
        return self._get_batch_custom(endpoint, continuation_token, include_recent_changes)
    
    def get_incremental(self,
                       continuation_token: Optional[str] = None,
                       include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve all invoices from a continuation point
        
        Args:
            continuation_token: Token from previous export to continue from
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with all data from continuation point and final token
        """
        endpoint = f"{self.config.base_url}/accounting/v2/tenant/{self.config.tenant_id}/export/invoices"
        return self._get_all_pages_custom(endpoint, continuation_token, include_recent_changes)
    
    def get_test(self) -> ExportResponse:
        """
        Retrieve single batch of invoices for testing
        
        Returns:
            ExportResponse with test data
        """
        endpoint = f"{self.config.base_url}/accounting/v2/tenant/{self.config.tenant_id}/export/invoices"
        return self._get_batch_custom(endpoint)

    # Additional transactional endpoints for invoice details
    def get_invoice_by_id(self, invoice_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific invoice
        
        Args:
            invoice_id: The ID of the invoice
        
        Returns:
            Detailed invoice information
        """
        url = f"{self.config.base_url}/accounting/v2/tenant/{self.config.tenant_id}/invoices/{invoice_id}"
        response = requests.get(url, headers=self.auth.headers)
        response.raise_for_status()
        return response.json()

