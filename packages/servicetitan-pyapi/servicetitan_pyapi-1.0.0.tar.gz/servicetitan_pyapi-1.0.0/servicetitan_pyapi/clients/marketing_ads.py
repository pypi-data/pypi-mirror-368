# servicetitan_pyapi/clients/marketing_ads.py
"""
ServiceTitan Marketing Ads API
Single Responsibility: Handle marketing ads attribution and lead tracking
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
from ..base import BaseClient


class MarketingAdsClient(BaseClient):
    """Client for ServiceTitan Marketing Ads endpoints"""
    
    def get_attributed_leads(self,
                            from_date: datetime,
                            to_date: datetime,
                            lead_type: Optional[str] = None,
                            page: int = 1,
                            page_size: int = 100,
                            include_total: bool = False) -> Dict[str, Any]:
        """
        Get attributed leads with marketing source information
        
        Args:
            from_date: Start date for lead records (UTC)
            to_date: End date for lead records (UTC)
            lead_type: Filter by lead type (e.g., 'Call', 'Form', 'Chat')
            page: Page number for pagination
            page_size: Number of items per page (max 100)
            include_total: Include total count in response
        
        Returns:
            Dict containing attributed leads data and pagination info
        """
        params = {
            'fromUtc': from_date.isoformat() + 'Z' if from_date.tzinfo is None else from_date.isoformat(),
            'toUtc': to_date.isoformat() + 'Z' if to_date.tzinfo is None else to_date.isoformat(),
            'page': page,
            'pageSize': min(page_size, 100)
        }
        
        if lead_type:
            params['leadType'] = lead_type
        
        if include_total:
            params['includeTotal'] = 'true'
        
        # Marketing Ads endpoints are under marketingads/v2
        url = f"{self.config.base_url}/marketingads/v2/tenant/{self.config.tenant_id}/attributed-leads"
        response = requests.get(url, headers=self.auth.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_all_attributed_leads(self,
                                from_date: datetime,
                                to_date: datetime,
                                lead_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all attributed leads for a date range, handling pagination automatically
        
        Args:
            from_date: Start date for lead records (UTC)
            to_date: End date for lead records (UTC)
            lead_type: Filter by lead type (e.g., 'Call', 'Form', 'Chat')
        
        Returns:
            List of all attributed leads
        """
        all_leads = []
        page = 1
        
        while True:
            response = self.get_attributed_leads(
                from_date=from_date,
                to_date=to_date,
                lead_type=lead_type,
                page=page,
                page_size=100
            )
            
            data = response.get('data', [])
            all_leads.extend(data)
            
            # Check if there are more pages
            if not response.get('hasMore', False):
                break
                
            page += 1
        
        return all_leads
    
    def get_lead_attribution_summary(self,
                                    from_date: datetime,
                                    to_date: datetime) -> Dict[str, Any]:
        """
        Get summary of lead attribution by source
        
        Args:
            from_date: Start date for analysis
            to_date: End date for analysis
        
        Returns:
            Summary of leads by attribution source
        """
        leads = self.get_all_attributed_leads(from_date, to_date)
        
        summary = {
            'total_leads': len(leads),
            'by_type': {},
            'by_source': {},
            'by_campaign': {},
            'with_jobs': 0,
            'with_estimates': 0,
            'revenue_generated': 0
        }
        
        for lead in leads:
            # Count by lead type
            lead_type = lead.get('leadType', 'Unknown')
            summary['by_type'][lead_type] = summary['by_type'].get(lead_type, 0) + 1
            
            # Count by attribution source
            source = lead.get('attributionSource', 'Unknown')
            if source not in summary['by_source']:
                summary['by_source'][source] = {
                    'count': 0,
                    'converted': 0,
                    'revenue': 0
                }
            summary['by_source'][source]['count'] += 1
            
            # Count by campaign
            campaign_name = lead.get('campaignName', 'Unknown')
            if campaign_name not in summary['by_campaign']:
                summary['by_campaign'][campaign_name] = {
                    'count': 0,
                    'converted': 0,
                    'revenue': 0
                }
            summary['by_campaign'][campaign_name]['count'] += 1
            
            # Track conversions
            if lead.get('jobId'):
                summary['with_jobs'] += 1
                summary['by_source'][source]['converted'] += 1
                summary['by_campaign'][campaign_name]['converted'] += 1
            
            if lead.get('estimateId'):
                summary['with_estimates'] += 1
            
            # Track revenue if available
            revenue = lead.get('revenue', 0)
            if revenue:
                summary['revenue_generated'] += revenue
                summary['by_source'][source]['revenue'] += revenue
                summary['by_campaign'][campaign_name]['revenue'] += revenue
        
        return summary
