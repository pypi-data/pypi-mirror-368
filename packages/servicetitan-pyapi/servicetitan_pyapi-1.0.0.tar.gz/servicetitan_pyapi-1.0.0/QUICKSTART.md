# ServiceTitan Python API - Quick Start Guide

This guide will help you get started with the ServiceTitan Python API library quickly.

## 🚀 Installation

### From PyPI (When Available)
```bash
pip install servicetitan-pyapi
```

### From GitHub (Public Repository)
```bash
# Latest version
pip install git+https://github.com/n90-co/servicetitan-pyapi.git

# Specific version
pip install git+https://github.com/n90-co/servicetitan-pyapi.git@v1.0.0

# With notebook support for analysis
pip install "git+https://github.com/n90-co/servicetitan-pyapi.git[notebooks]"
```

### Development Setup
```bash
git clone https://github.com/n90-co/servicetitan-pyapi.git
cd servicetitan-pyapi
pip install -e ".[dev]"
```

## 🔑 Authentication Setup

1. **Get ServiceTitan API Credentials**
   - Log in to your ServiceTitan account
   - Navigate to Settings > Integrations > API Access
   - Create a new API application or use existing credentials

2. **Configure Authentication**
   
   Create a configuration file or set environment variables:
   
   ```python
   # config/servicetitan_config.json
   {
       "client_id": "your_client_id",
       "client_secret": "your_client_secret",
       "tenant_id": "your_tenant_id",
       "app_key": "your_app_key"
   }
   ```

## 💡 Basic Usage

```python
from servicetitan_pyapi import ServiceTitanAPI

# Initialize the API client
api = ServiceTitanAPI(config_path="config/servicetitan_config.json")

# Get customer data
customers = api.customers.get_customers(limit=10)
print(f"Found {len(customers)} customers")

# Get job information
jobs = api.jobs.get_jobs(limit=5)
for job in jobs:
    print(f"Job #{job.get('number')}: {job.get('summary')}")

# Search for specific data
recent_calls = api.calls.get_calls(
    created_on_or_after="2024-01-01T00:00:00Z",
    limit=20
)
```

## 🎯 Common Use Cases

### Customer Management
```python
# Get all customers
customers = api.customers.get_customers()

# Get customer by ID
customer = api.customers.get_customer(customer_id=12345)

# Search customers
results = api.customers.search_customers(query="John Smith")
```

### Job Tracking
```python
# Get recent jobs
jobs = api.jobs.get_jobs(
    created_on_or_after="2024-01-01T00:00:00Z",
    page_size=50
)

# Get job details
job_detail = api.jobs.get_job(job_id=67890)

# Get job history
history = api.jobs.get_job_history(job_id=67890)
```

### Marketing Analytics
```python
# Get marketing campaigns
campaigns = api.marketing.get_campaigns()

# Get ad performance
ads_data = api.marketing_ads.get_ads_data(
    date_from="2024-01-01",
    date_to="2024-01-31"
)
```

## 🔧 Advanced Features

### Custom Endpoints
```python
# Use custom API endpoints not covered by standard clients
response = api.base_client.custom_get("/custom/endpoint")
custom_data = api.base_client.custom_post("/custom/action", data={"key": "value"})
```

### Error Handling
```python
from servicetitan_pyapi.utils.exceptions import ServiceTitanAPIError

try:
    customers = api.customers.get_customers()
except ServiceTitanAPIError as e:
    print(f"API Error: {e}")
    # Handle error appropriately
```

### Pagination
```python
# Automatic pagination handling
all_customers = []
for page in api.customers.get_customers_paginated():
    all_customers.extend(page)
    print(f"Processed {len(all_customers)} customers so far...")
```

## 📊 Data Export Example

```python
import pandas as pd

# Export customer data to CSV
customers = api.customers.get_customers(limit=1000)
df = pd.DataFrame(customers)
df.to_csv("customers_export.csv", index=False)

# Export job data with date filtering
jobs = api.jobs.get_jobs(
    created_on_or_after="2024-01-01T00:00:00Z",
    limit=500
)
jobs_df = pd.DataFrame(jobs)
jobs_df.to_csv("jobs_2024.csv", index=False)
```

## 🚨 Important Notes

- **Rate Limiting**: ServiceTitan API has rate limits. The library handles basic rate limiting, but monitor your usage.
- **Data Sensitivity**: Customer and business data is sensitive. Follow your organization's data handling policies.
- **API Versions**: This library targets ServiceTitan API v2. Check compatibility with your ServiceTitan instance.
- **Token Management**: OAuth tokens are automatically refreshed. Ensure your credentials remain valid.

## 🆘 Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```python
   # Verify credentials
   api.auth.verify_credentials()
   ```

2. **Network Timeouts**
   ```python
   # Increase timeout
   api = ServiceTitanAPI(config_path="config.json", timeout=60)
   ```

3. **Large Data Sets**
   ```python
   # Use pagination for large requests
   for page in api.customers.get_customers_paginated(page_size=100):
       process_page(page)
   ```

## 📞 Support

- **Documentation**: [GitHub README](https://github.com/n90-co/servicetitan-pyapi#readme)
- **Issues**: [GitHub Issues](https://github.com/n90-co/servicetitan-pyapi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/n90-co/servicetitan-pyapi/discussions)

Happy coding! 🎉
