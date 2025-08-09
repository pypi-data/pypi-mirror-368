# servicetitan_pyapi/clients/jobs.py
"""
ServiceTitan Jobs API
Single Responsibility: Handle job-related API calls
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
from ..base import BaseClient, ExportResponse


class JobsClient(BaseClient):
    """Client for ServiceTitan Jobs endpoints"""
    
    # Export endpoint methods
    def get_all(self) -> ExportResponse:
        """
        Retrieve all jobs from ServiceTitan (from the beginning)
        
        Returns:
            ExportResponse with all job data and final continuation token
        """
        # Jobs are under jpm/v2
        endpoint = f"{self.config.base_url}/jpm/v2/tenant/{self.config.tenant_id}/export/jobs"
        return self._get_all_pages_custom(endpoint)
    
    def get_batch(self,
                  continuation_token: Optional[str] = None,
                  include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve a single batch of jobs
        
        Args:
            continuation_token: Token from previous export's continuation_token
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with batch data and continuation token for next call
        """
        endpoint = f"{self.config.base_url}/jpm/v2/tenant/{self.config.tenant_id}/export/jobs"
        return self._get_batch_custom(endpoint, continuation_token, include_recent_changes)
    
    def get_incremental(self,
                       continuation_token: Optional[str] = None,
                       include_recent_changes: bool = False) -> ExportResponse:
        """
        Retrieve all jobs from a continuation point
        
        Args:
            continuation_token: Token from previous export to continue from
            include_recent_changes: If True, get recent changes quicker but may see duplicates
        
        Returns:
            ExportResponse with all data from continuation point and final token
        """
        endpoint = f"{self.config.base_url}/jpm/v2/tenant/{self.config.tenant_id}/export/jobs"
        return self._get_all_pages_custom(endpoint, continuation_token, include_recent_changes)
    
    def get_test(self) -> ExportResponse:
        """
        Retrieve single batch of jobs for testing
        
        Returns:
            ExportResponse with test data
        """
        endpoint = f"{self.config.base_url}/jpm/v2/tenant/{self.config.tenant_id}/export/jobs"
        return self._get_batch_custom(endpoint)

    # Additional transactional endpoints for job details(if needed)
    def get_job_by_id(self, job_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific job
        
        Args:
            job_id: The ID of the job
        
        Returns:
            Detailed job information
        """
        # Individual job endpoint might still be under jbce/v2 or jpm/v2
        # Try jpm/v2 first to match the export endpoint
        url = f"{self.config.base_url}/jpm/v2/tenant/{self.config.tenant_id}/jobs/{job_id}"
        response = requests.get(url, headers=self.auth.headers)
        response.raise_for_status()
        return response.json()
