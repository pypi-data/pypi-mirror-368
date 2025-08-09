"""
ServiceTitan Python API Client Library

A comprehensive Python client for interacting with the ServiceTitan API.
"""

from .auth import ServiceTitanConfig, ServiceTitanAuth
from .base import BaseClient, ExportResponse

# Import all clients
from .clients.customers import CustomersClient
from .clients.locations import LocationsClient
from .clients.bookings import BookingsClient
from .clients.leads import LeadsClient
from .clients.calls import CallsClient
from .clients.jobs import JobsClient
from .clients.estimates import EstimatesClient
from .clients.appointments import AppointmentsClient
from .clients.invoices import InvoicesClient
from .clients.marketing import MarketingClient
from .clients.marketing_ads import MarketingAdsClient
from .clients.settings import SettingsClient

# Version
__version__ = "1.0.0"

# Public API
__all__ = [
    # Core
    "ServiceTitanConfig",
    "ServiceTitanAuth",
    "BaseClient",
    "ExportResponse",
    # Clients
    "CustomersClient",
    "LocationsClient",
    "BookingsClient",
    "LeadsClient",
    "CallsClient",
    "JobsClient",
    "EstimatesClient",
    "AppointmentsClient",
    "InvoicesClient",
    "MarketingClient",
    "MarketingAdsClient",
    "SettingsClient",
]

# Convenience class for easy access to all clients
class ServiceTitanAPI:
    """
    Convenience wrapper that initializes all clients.
    
    Usage:
        api = ServiceTitanAPI("config.json")
        customers = api.customers.get_all()
    """
    
    def __init__(self, config_path: str = "servicetitan_config.json"):
        self.config = ServiceTitanConfig.from_file(config_path)
        self.auth = ServiceTitanAuth(self.config)
        
        # Initialize all clients
        self.customers = CustomersClient(self.auth)
        self.locations = LocationsClient(self.auth)
        self.bookings = BookingsClient(self.auth)
        self.leads = LeadsClient(self.auth)
        self.calls = CallsClient(self.auth)
        self.jobs = JobsClient(self.auth)
        self.estimates = EstimatesClient(self.auth)
        self.appointments = AppointmentsClient(self.auth)
        self.invoices = InvoicesClient(self.auth)
        self.marketing = MarketingClient(self.auth)
        self.marketing_ads = MarketingAdsClient(self.auth)
        self.settings = SettingsClient(self.auth)
        