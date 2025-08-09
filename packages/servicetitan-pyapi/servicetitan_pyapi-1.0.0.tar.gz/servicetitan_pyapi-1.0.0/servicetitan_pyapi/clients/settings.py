# servicetitan_pyapi/clients/settings.py
"""
ServiceTitan Settings API
Single Responsibility: Handle settings/reference data API calls
"""

from typing import Optional, List, Dict, Any
from ..base import BaseClient, ExportResponse


class SettingsClient(BaseClient):
    """Client for ServiceTitan Settings endpoints - reference data"""
    
    # Business Units
    def get_all_business_units(self) -> ExportResponse:
        """
        Retrieve all business units from ServiceTitan
        
        Returns:
            ExportResponse with all business unit data and final continuation token
        """
        # Business units are under settings/v2
        endpoint = f"{self.config.base_url}/settings/v2/tenant/{self.config.tenant_id}/export/business-units"
        return self._get_all_pages_custom(endpoint)
    
    def get_business_units_batch(self,
                                 continuation_token: Optional[str] = None,
                                 include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve a single batch of business units
        
        Returns:
            ExportResponse with batch data and continuation token
        """
        endpoint = f"{self.config.base_url}/settings/v2/tenant/{self.config.tenant_id}/export/business-units"
        return self._get_batch_custom(endpoint, continuation_token, include_recent_changes)
    
    # Employees
    def get_all_employees(self) -> ExportResponse:
        """
        Retrieve all employees from ServiceTitan
        
        Returns:
            ExportResponse with all employee data and final continuation token
        """
        endpoint = f"{self.config.base_url}/settings/v2/tenant/{self.config.tenant_id}/export/employees"
        return self._get_all_pages_custom(endpoint)
    
    def get_employees_batch(self,
                           continuation_token: Optional[str] = None,
                           include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve a single batch of employees
        
        Returns:
            ExportResponse with batch data and continuation token
        """
        endpoint = f"{self.config.base_url}/settings/v2/tenant/{self.config.tenant_id}/export/employees"
        return self._get_batch_custom(endpoint, continuation_token, include_recent_changes)
    
    # Tag Types
    def get_all_tag_types(self) -> ExportResponse:
        """
        Retrieve all tag types from ServiceTitan
        
        Returns:
            ExportResponse with all tag type data and final continuation token
        """
        endpoint = f"{self.config.base_url}/settings/v2/tenant/{self.config.tenant_id}/export/tag-types"
        return self._get_all_pages_custom(endpoint)
    
    def get_tag_types_batch(self,
                           continuation_token: Optional[str] = None,
                           include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve a single batch of tag types
        
        Returns:
            ExportResponse with batch data and continuation token
        """
        endpoint = f"{self.config.base_url}/settings/v2/tenant/{self.config.tenant_id}/export/tag-types"
        return self._get_batch_custom(endpoint, continuation_token, include_recent_changes)
    
    # Technicians
    def get_all_technicians(self) -> ExportResponse:
        """
        Retrieve all technicians from ServiceTitan
        
        Returns:
            ExportResponse with all technician data and final continuation token
        """
        endpoint = f"{self.config.base_url}/settings/v2/tenant/{self.config.tenant_id}/export/technicians"
        return self._get_all_pages_custom(endpoint)
    
    def get_technicians_batch(self,
                             continuation_token: Optional[str] = None,
                             include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve a single batch of technicians
        
        Returns:
            ExportResponse with batch data and continuation token
        """
        endpoint = f"{self.config.base_url}/settings/v2/tenant/{self.config.tenant_id}/export/technicians"
        return self._get_batch_custom(endpoint, continuation_token, include_recent_changes)
    
    # Convenience method to get all reference data at once
    def get_all_reference_data(self) -> Dict[str, Any]:
        """
        Get all reference data in one call - useful for initial setup
        
        Returns:
            Dictionary with all reference data organized by type
        """
        return {
            'business_units': self.get_all_business_units().data,
            'employees': self.get_all_employees().data,
            'tag_types': self.get_all_tag_types().data,
            'technicians': self.get_all_technicians().data
        }
    
    # Helper methods to create lookup dictionaries
    def create_lookup_tables(self) -> Dict[str, Dict]:
        """
        Create lookup dictionaries for easy ID-to-name resolution
        
        Returns:
            Dictionary of lookup tables for each reference type
        """
        reference_data = self.get_all_reference_data()
        
        lookups = {
            'business_units': {bu['id']: bu['name'] for bu in reference_data['business_units']},
            'employees': {emp['id']: f"{emp.get('firstName', '')} {emp.get('lastName', '')}" 
                         for emp in reference_data['employees']},
            'technicians': {tech['id']: tech.get('name', f"Tech {tech['id']}") 
                           for tech in reference_data['technicians']},
            'tag_types': {tag['id']: tag['name'] for tag in reference_data['tag_types']}
        }
        
        return lookups

