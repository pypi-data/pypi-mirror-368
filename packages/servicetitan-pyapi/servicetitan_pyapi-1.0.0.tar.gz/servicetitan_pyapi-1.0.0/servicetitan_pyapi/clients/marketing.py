# servicetitan_pyapi/clients/marketing.py
"""
ServiceTitan Marketing API
Single Responsibility: Handle marketing campaign and attribution API calls
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
from ..base import BaseClient, ExportResponse


class MarketingClient(BaseClient):
    """Client for ServiceTitan Marketing endpoints"""
    
    # Campaign endpoints (transactional)
    def get_campaigns(self,
                     active_only: bool = True,
                     page: int = 1,
                     page_size: int = 100) -> Dict[str, Any]:
        """
        Get marketing campaigns from ServiceTitan
        
        Args:
            active_only: If True, only return active campaigns
            page: Page number for pagination
            page_size: Number of items per page (max 100)
        
        Returns:
            Dict containing campaigns data and pagination info
        """
        params: Dict[str, Any] = {
            'page': page,
            'pageSize': min(page_size, 100)
        }
        
        if active_only:
            params['active'] = 'true'
        
        # Marketing endpoints are under marketing/v2
        url = f"{self.config.base_url}/marketing/v2/tenant/{self.config.tenant_id}/campaigns"
        response = requests.get(url, headers=self.auth.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_all_campaigns(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all campaigns, handling pagination automatically
        
        Args:
            active_only: If True, only return active campaigns
        
        Returns:
            List of all campaigns
        """
        all_campaigns = []
        page = 1
        
        while True:
            response = self.get_campaigns(active_only=active_only, page=page, page_size=100)
            
            data = response.get('data', [])
            all_campaigns.extend(data)
            
            if not response.get('hasMore', False):
                break
                
            page += 1
        
        return all_campaigns
    
    def get_campaign_by_id(self, campaign_id: int) -> Dict[str, Any]:
        """
        Get a specific campaign by ID
        
        Args:
            campaign_id: The ID of the campaign
        
        Returns:
            Campaign details
        """
        url = f"{self.config.base_url}/marketing/v2/tenant/{self.config.tenant_id}/campaigns/{campaign_id}"
        response = requests.get(url, headers=self.auth.headers)
        response.raise_for_status()
        return response.json()
    
    # Category endpoints (for lead sources)
    def get_categories(self,
                      active_only: bool = True,
                      page: int = 1,
                      page_size: int = 100) -> Dict[str, Any]:
        """
        Get marketing categories (lead sources)
        
        Args:
            active_only: If True, only return active categories
            page: Page number for pagination
            page_size: Number of items per page (max 100)
        
        Returns:
            Dict containing categories data and pagination info
        """
        params: Dict[str, Any] = {
            'page': page,
            'pageSize': min(page_size, 100)
        }
        
        if active_only:
            params['active'] = 'true'
        
        url = f"{self.config.base_url}/marketing/v2/tenant/{self.config.tenant_id}/categories"
        response = requests.get(url, headers=self.auth.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_all_categories(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all categories, handling pagination automatically
        
        Args:
            active_only: If True, only return active categories
        
        Returns:
            List of all categories (lead sources)
        """
        all_categories = []
        page = 1
        
        while True:
            response = self.get_categories(active_only=active_only, page=page, page_size=100)
            
            data = response.get('data', [])
            all_categories.extend(data)
            
            if not response.get('hasMore', False):
                break
                
            page += 1
        
        return all_categories
    
    # Campaign costs (for ROI tracking)
    def get_campaign_costs(self,
                          campaign_id: int,
                          from_date: Optional[datetime] = None,
                          to_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get costs for a specific campaign
        
        Args:
            campaign_id: The ID of the campaign
            from_date: Start date for cost records
            to_date: End date for cost records
        
        Returns:
            List of campaign costs
        """
        params = {}
        if from_date:
            params['from'] = from_date.isoformat()
        if to_date:
            params['to'] = to_date.isoformat()
        
        url = f"{self.config.base_url}/marketing/v2/tenant/{self.config.tenant_id}/campaigns/{campaign_id}/costs"
        response = requests.get(url, headers=self.auth.headers, params=params)
        response.raise_for_status()
        return response.json().get('data', [])

