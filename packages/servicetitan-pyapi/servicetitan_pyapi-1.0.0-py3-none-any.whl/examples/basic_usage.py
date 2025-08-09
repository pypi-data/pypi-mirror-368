#!/usr/bin/env python3
"""
Basic usage examples for the ServiceTitan Python API client.
"""

from servicetitan_pyapi import ServiceTitanAPI
from datetime import datetime, timedelta


def main():
    # Initialize API
    api = ServiceTitanAPI("config/servicetitan_config.json")
    
    # Get reference data for lookups
    print("Loading reference data...")
    lookups = api.settings.create_lookup_tables()
    
    # Get recent customers
    print("\nFetching recent customers...")
    customers = api.customers.get_test()
    print(f"Found {len(customers)} customers")
    
    # Get jobs from last 7 days
    print("\nFetching recent jobs...")
    jobs = api.jobs.get_batch()
    
    # Display jobs with business unit names
    for job in jobs.data[:5]:
        bu_id = job.get('businessUnitId')
        bu_name = lookups['business_units'].get(bu_id, 'Unknown')
        print(f"  Job {job['id']}: {bu_name}")
    
    # Track conversions
    print("\nAnalyzing conversions...")
    leads = api.leads.get_batch()
    estimates = api.estimates.get_batch()
    invoices = api.invoices.get_batch()
    
    print(f"  Leads: {len(leads)}")
    print(f"  Estimates: {len(estimates)}")
    print(f"  Invoices: {len(invoices)}")
    
    # Calculate revenue
    total_revenue = sum(i.get('total', 0) for i in invoices.data)
    print(f"  Total Revenue: ${total_revenue:,.2f}")


if __name__ == "__main__":
    main()