# servicetitan_pyapi/clients/appointments.py
"""
ServiceTitan Appointments API
Single Responsibility: Handle appointment-related API calls
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
from ..base import BaseClient, ExportResponse


class AppointmentsClient(BaseClient):
    """Client for ServiceTitan Appointments endpoints"""
    
    # Export endpoint methods
    def get_all(self) -> ExportResponse:
        """
        Retrieve all appointments from ServiceTitan (from the beginning)
        
        Returns:
            ExportResponse with all appointment data and final continuation token
        """
        # Appointments are under jpm/v2 (Job Planning & Management)
        endpoint = f"{self.config.base_url}/jpm/v2/tenant/{self.config.tenant_id}/export/appointments"
        return self._get_all_pages_custom(endpoint)
    
    def get_batch(self,
                  continuation_token: Optional[str] = None,
                  include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve a single batch of appointments
        
        Args:
            continuation_token: Token from previous export's continuation_token
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with batch data and continuation token for next call
        """
        endpoint = f"{self.config.base_url}/jpm/v2/tenant/{self.config.tenant_id}/export/appointments"
        return self._get_batch_custom(endpoint, continuation_token, include_recent_changes)
    
    def get_incremental(self,
                       continuation_token: Optional[str] = None,
                       include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve all appointments from a continuation point
        
        Args:
            continuation_token: Token from previous export to continue from
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with all data from continuation point and final token
        """
        endpoint = f"{self.config.base_url}/jpm/v2/tenant/{self.config.tenant_id}/export/appointments"
        return self._get_all_pages_custom(endpoint, continuation_token, include_recent_changes)
    
    def get_test(self) -> ExportResponse:
        """
        Retrieve single batch of appointments for testing
        
        Returns:
            ExportResponse with test data
        """
        endpoint = f"{self.config.base_url}/jpm/v2/tenant/{self.config.tenant_id}/export/appointments"
        return self._get_batch_custom(endpoint)

    # Additional transactional endpoints for appointment details
    def get_appointment_by_id(self, appointment_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific appointment
        
        Args:
            appointment_id: The ID of the appointment
        
        Returns:
            Detailed appointment information
        """
        url = f"{self.config.base_url}/jpm/v2/tenant/{self.config.tenant_id}/appointments/{appointment_id}"
        response = requests.get(url, headers=self.auth.headers)
        response.raise_for_status()
        return response.json()

