#!/usr/bin/env python3
"""
marketing_roi.py - Marketing ROI Analysis Example

Demonstrates how to calculate return on investment for marketing campaigns
by tracking leads through to actual revenue.
"""

from servicetitan_pyapi import ServiceTitanAPI
from servicetitan_pyapi.utils import (
    calculate_date_range,
    export_to_csv,
    filter_by_date,
    calculate_metrics,
    parse_datetime
)
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json


class MarketingROIAnalyzer:
    """Analyze marketing campaign ROI using ServiceTitan data."""
    
    def __init__(self, config_path: str = "config/servicetitan_config.json"):
        """Initialize the analyzer with ServiceTitan API."""
        self.api = ServiceTitanAPI(config_path)
        self.lookups = None
        
    def load_reference_data(self):
        """Load reference data for name resolution."""
        print("Loading reference data...")
        self.lookups = self.api.settings.create_lookup_tables()
        return self.lookups
    
    def analyze_campaign_performance(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze marketing campaign performance and ROI.
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing campaign metrics
        """
        print(f"\n=== MARKETING CAMPAIGN ANALYSIS ({days_back} days) ===")
        
        # Get date range
        start_date, end_date = calculate_date_range(days_back)
        
        # Get campaigns and categories
        print("Fetching campaigns and categories...")
        campaigns = self.api.marketing.get_all_campaigns()
        categories = self.api.marketing.get_all_categories()
        
        # Create category lookup
        category_lookup = {cat['id']: cat['name'] for cat in categories}
        
        # Get leads, jobs, and invoices
        print("Fetching leads, jobs, and invoices...")
        leads = self.api.leads.get_batch().data
        jobs = self.api.jobs.get_batch().data
        invoices = self.api.invoices.get_batch().data
        
        # Filter by date
        recent_leads = filter_by_date(leads, 'createdOn', start_date, end_date)
        recent_jobs = filter_by_date(jobs, 'createdOn', start_date, end_date)
        recent_invoices = filter_by_date(invoices, 'createdOn', start_date, end_date)
        
        print(f"Found {len(recent_leads)} leads, {len(recent_jobs)} jobs, {len(recent_invoices)} invoices")
        
        # Calculate revenue by job
        job_revenue = {}
        for invoice in recent_invoices:
            job_id = invoice.get('jobId')
            if job_id:
                job_revenue[job_id] = job_revenue.get(job_id, 0) + invoice.get('total', 0)
        
        # Analyze by campaign
        campaign_metrics = {}
        
        for campaign in campaigns:
            campaign_id = campaign['id']
            campaign_name = campaign['name']
            category_name = category_lookup.get(campaign.get('categoryId'), 'Unknown')
            
            # Count leads from this campaign
            campaign_leads = [l for l in recent_leads if l.get('campaignId') == campaign_id]
            campaign_jobs = [j for j in recent_jobs if j.get('campaignId') == campaign_id]
            
            # Calculate revenue
            campaign_revenue = sum(
                job_revenue.get(job['id'], 0) 
                for job in campaign_jobs 
                if job.get('id') in job_revenue
            )
            
            # Get campaign costs
            costs = self.api.marketing.get_campaign_costs(
                campaign_id,
                from_date=start_date,
                to_date=end_date
            )
            total_cost = sum(c.get('amount', 0) for c in costs)
            
            # Calculate metrics
            lead_count = len(campaign_leads)
            job_count = len(campaign_jobs)
            
            campaign_metrics[campaign_name] = {
                'category': category_name,
                'leads': lead_count,
                'jobs': job_count,
                'revenue': campaign_revenue,
                'cost': total_cost,
                'conversion_rate': (job_count / lead_count * 100) if lead_count > 0 else 0,
                'cost_per_lead': total_cost / lead_count if lead_count > 0 else 0,
                'cost_per_job': total_cost / job_count if job_count > 0 else 0,
                'revenue_per_job': campaign_revenue / job_count if job_count > 0 else 0,
                'roi': ((campaign_revenue - total_cost) / total_cost * 100) if total_cost > 0 else float('inf'),
                'profit': campaign_revenue - total_cost
            }
        
        return campaign_metrics
    
    def analyze_lead_sources(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze performance by lead source type.
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing source metrics
        """
        print(f"\n=== LEAD SOURCE ANALYSIS ({days_back} days) ===")
        
        # Get date range
        start_date, end_date = calculate_date_range(days_back)
        
        # Get data
        print("Fetching calls, bookings, and leads...")
        calls = self.api.calls.get_batch().data
        bookings = self.api.bookings.get_batch().data
        leads = self.api.leads.get_batch().data
        
        # Filter by date
        recent_calls = filter_by_date(calls, 'createdOn', start_date, end_date)
        recent_bookings = filter_by_date(bookings, 'createdOn', start_date, end_date)
        recent_leads = filter_by_date(leads, 'createdOn', start_date, end_date)
        
        # Analyze by source type
        source_metrics = {
            'Phone Calls': {
                'count': len([c for c in recent_calls if c.get('direction') == 'Inbound']),
                'converted': len([c for c in recent_calls if c.get('jobId')]),
                'source_type': 'Inbound Communication'
            },
            'Web Forms': {
                'count': len(recent_bookings),
                'converted': len([b for b in recent_bookings if b.get('status') == 'Booked']),
                'source_type': 'Digital'
            },
            'Direct Leads': {
                'count': len(recent_leads),
                'converted': len([l for l in recent_leads if l.get('status') in ['Won', 'Converted']]),
                'source_type': 'Mixed'
            }
        }
        
        # Calculate conversion rates
        for source, metrics in source_metrics.items():
            if metrics['count'] > 0:
                metrics['conversion_rate'] = metrics['converted'] / metrics['count'] * 100
            else:
                metrics['conversion_rate'] = 0
        
        return source_metrics
    
    def generate_roi_report(self, days_back: int = 30, export: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive ROI report.
        
        Args:
            days_back: Number of days to analyze
            export: Whether to export to CSV
            
        Returns:
            Complete ROI analysis
        """
        print(f"\n{'='*60}")
        print(f"MARKETING ROI REPORT - Last {days_back} Days")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Load reference data if not loaded
        if not self.lookups:
            self.load_reference_data()
        
        # Get campaign performance
        campaign_metrics = self.analyze_campaign_performance(days_back)
        
        # Get lead source performance
        source_metrics = self.analyze_lead_sources(days_back)
        
        # Sort campaigns by ROI
        sorted_campaigns = sorted(
            campaign_metrics.items(),
            key=lambda x: x[1]['profit'],
            reverse=True
        )
        
        # Print top performing campaigns
        print("\n📊 TOP PERFORMING CAMPAIGNS BY PROFIT:")
        print("-" * 60)
        
        for i, (campaign_name, metrics) in enumerate(sorted_campaigns[:10], 1):
            roi_display = f"{metrics['roi']:.1f}%" if metrics['roi'] != float('inf') else "∞"
            
            print(f"\n{i}. {campaign_name} ({metrics['category']})")
            print(f"   Revenue: ${metrics['revenue']:,.2f}")
            print(f"   Cost: ${metrics['cost']:,.2f}")
            print(f"   Profit: ${metrics['profit']:,.2f}")
            print(f"   ROI: {roi_display}")
            print(f"   Leads: {metrics['leads']} → Jobs: {metrics['jobs']} ({metrics['conversion_rate']:.1f}%)")
            
            if metrics['jobs'] > 0:
                print(f"   Cost per Job: ${metrics['cost_per_job']:,.2f}")
                print(f"   Revenue per Job: ${metrics['revenue_per_job']:,.2f}")
        
        # Print lead source analysis
        print("\n📞 LEAD SOURCE PERFORMANCE:")
        print("-" * 60)
        
        for source, metrics in source_metrics.items():
            print(f"\n{source}:")
            print(f"   Total: {metrics['count']}")
            print(f"   Converted: {metrics['converted']}")
            print(f"   Conversion Rate: {metrics['conversion_rate']:.1f}%")
        
        # Calculate totals
        total_revenue = sum(m['revenue'] for m in campaign_metrics.values())
        total_cost = sum(m['cost'] for m in campaign_metrics.values())
        total_profit = total_revenue - total_cost
        total_leads = sum(m['leads'] for m in campaign_metrics.values())
        total_jobs = sum(m['jobs'] for m in campaign_metrics.values())
        
        # Print summary
        print("\n💰 OVERALL MARKETING PERFORMANCE:")
        print("-" * 60)
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print(f"Total Cost: ${total_cost:,.2f}")
        print(f"Total Profit: ${total_profit:,.2f}")
        print(f"Overall ROI: {((total_profit / total_cost * 100) if total_cost > 0 else 0):.1f}%")
        print(f"Total Leads: {total_leads}")
        print(f"Total Jobs: {total_jobs}")
        print(f"Overall Conversion: {(total_jobs / total_leads * 100 if total_leads > 0 else 0):.1f}%")
        
        # Export to CSV if requested
        if export:
            # Prepare data for export
            export_data = []
            for campaign_name, metrics in campaign_metrics.items():
                export_data.append({
                    'Campaign': campaign_name,
                    'Category': metrics['category'],
                    'Leads': metrics['leads'],
                    'Jobs': metrics['jobs'],
                    'Revenue': metrics['revenue'],
                    'Cost': metrics['cost'],
                    'Profit': metrics['profit'],
                    'ROI_Percent': metrics['roi'] if metrics['roi'] != float('inf') else 999999,
                    'Conversion_Rate': metrics['conversion_rate'],
                    'Cost_Per_Lead': metrics['cost_per_lead'],
                    'Cost_Per_Job': metrics['cost_per_job'],
                    'Revenue_Per_Job': metrics['revenue_per_job']
                })
            
            filename = f"marketing_roi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            export_to_csv(export_data, filename)
            print(f"\n📁 Report exported to: {filename}")
        
        return {
            'campaign_metrics': campaign_metrics,
            'source_metrics': source_metrics,
            'summary': {
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'overall_roi': (total_profit / total_cost * 100) if total_cost > 0 else 0,
                'total_leads': total_leads,
                'total_jobs': total_jobs,
                'overall_conversion': (total_jobs / total_leads * 100) if total_leads > 0 else 0
            }
        }


def main():
    """Run marketing ROI analysis."""
    # Initialize analyzer
    analyzer = MarketingROIAnalyzer()
    
    # Generate reports for different time periods
    periods = [7, 30, 90]
    
    for days in periods:
        report = analyzer.generate_roi_report(days_back=days, export=(days == 30))
        
        # Save summary to JSON
        summary_file = f"roi_summary_{days}days.json"
        with open(summary_file, 'w') as f:
            json.dump(report['summary'], f, indent=2, default=str)
        print(f"📊 Summary saved to: {summary_file}")
        
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()