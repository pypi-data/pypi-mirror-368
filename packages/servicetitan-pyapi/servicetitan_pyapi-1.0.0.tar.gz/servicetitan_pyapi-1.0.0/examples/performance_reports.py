#!/usr/bin/env python3
"""
performance_reports.py - Employee and Technician Performance Reports

Demonstrates how to analyze performance metrics for technicians, sales reps,
and other employees using ServiceTitan data.
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
from typing import Dict, List, Any, Optional
import json


class PerformanceReporter:
    """Generate performance reports for ServiceTitan employees and technicians."""
    
    def __init__(self, config_path: str = "config/servicetitan_config.json"):
        """Initialize the reporter with ServiceTitan API."""
        self.api = ServiceTitanAPI(config_path)
        self.lookups = None
        
    def load_reference_data(self):
        """Load reference data for name resolution."""
        print("Loading employee and technician data...")
        self.lookups = self.api.settings.create_lookup_tables()
        
        # Also get full employee/tech data for additional details
        self.employees = {e['id']: e for e in self.api.settings.get_all_employees().data}
        self.technicians = {t['id']: t for t in self.api.settings.get_all_technicians().data}
        self.business_units = {bu['id']: bu for bu in self.api.settings.get_all_business_units().data}
        
        return self.lookups
    
    def analyze_technician_performance(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze technician performance metrics.
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing technician metrics
        """
        print(f"\n=== TECHNICIAN PERFORMANCE ANALYSIS ({days_back} days) ===")
        
        # Get date range
        start_date, end_date = calculate_date_range(days_back)
        
        # Load reference data if not loaded
        if not self.lookups:
            self.load_reference_data()
        
        # Get appointments and jobs
        print("Fetching appointments and jobs...")
        appointments = self.api.appointments.get_batch().data
        jobs = self.api.jobs.get_batch().data
        invoices = self.api.invoices.get_batch().data
        
        # Filter by date
        recent_appointments = filter_by_date(appointments, 'start', start_date, end_date)
        recent_jobs = filter_by_date(jobs, 'createdOn', start_date, end_date)
        
        # Create job revenue lookup
        job_revenue = {}
        for invoice in invoices:
            job_id = invoice.get('jobId')
            if job_id:
                job_revenue[job_id] = job_revenue.get(job_id, 0) + invoice.get('total', 0)
        
        # Analyze by technician
        tech_performance = {}
        
        for appt in recent_appointments:
            tech_ids = appt.get('technicianIds', [])
            
            for tech_id in tech_ids:
                if self.lookups:
                    tech_name = self.lookups['technicians'].get(tech_id, f'Tech {tech_id}')
                else:
                    tech_name = f'Tech {tech_id}'

                if tech_name not in tech_performance:
                    tech_performance[tech_name] = {
                        'id': tech_id,
                        'appointments': 0,
                        'completed': 0,
                        'canceled': 0,
                        'total_hours': 0,
                        'revenue_generated': 0,
                        'jobs': set()
                    }
                
                tech_performance[tech_name]['appointments'] += 1
                
                # Track status
                status = appt.get('status', '').lower()
                if status in ['done', 'completed']:
                    tech_performance[tech_name]['completed'] += 1
                elif status == 'canceled':
                    tech_performance[tech_name]['canceled'] += 1
                
                # Calculate hours
                start_time = parse_datetime(appt.get('start'))
                end_time = parse_datetime(appt.get('end'))
                if start_time and end_time:
                    hours = (end_time - start_time).total_seconds() / 3600
                    tech_performance[tech_name]['total_hours'] += hours
                
                # Track jobs and revenue
                job_id = appt.get('jobId')
                if job_id:
                    tech_performance[tech_name]['jobs'].add(job_id)
                    if job_id in job_revenue:
                        # Split revenue among techs on the appointment
                        tech_performance[tech_name]['revenue_generated'] += job_revenue[job_id] / len(tech_ids)
        
        # Convert job sets to counts
        for tech_data in tech_performance.values():
            tech_data['job_count'] = len(tech_data['jobs'])
            del tech_data['jobs']  # Remove set for JSON serialization
            
            # Calculate efficiency metrics
            if tech_data['appointments'] > 0:
                tech_data['completion_rate'] = tech_data['completed'] / tech_data['appointments'] * 100
                tech_data['cancelation_rate'] = tech_data['canceled'] / tech_data['appointments'] * 100
            else:
                tech_data['completion_rate'] = 0
                tech_data['cancelation_rate'] = 0
            
            if tech_data['total_hours'] > 0:
                tech_data['revenue_per_hour'] = tech_data['revenue_generated'] / tech_data['total_hours']
            else:
                tech_data['revenue_per_hour'] = 0
        
        return tech_performance
    
    def analyze_sales_performance(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze sales rep performance metrics.
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing sales metrics
        """
        print(f"\n=== SALES PERFORMANCE ANALYSIS ({days_back} days) ===")
        
        # Get date range
        start_date, end_date = calculate_date_range(days_back)
        
        # Load reference data if not loaded
        if not self.lookups:
            self.load_reference_data()
        
        # Get estimates and leads
        print("Fetching estimates and leads...")
        estimates = self.api.estimates.get_batch().data
        leads = self.api.leads.get_batch().data
        jobs = self.api.jobs.get_batch().data
        
        # Filter by date
        recent_estimates = filter_by_date(estimates, 'createdOn', start_date, end_date)
        recent_leads = filter_by_date(leads, 'createdOn', start_date, end_date)
        recent_jobs = filter_by_date(jobs, 'createdOn', start_date, end_date)
        
        # Analyze by sales rep
        sales_performance = {}
        
        # Process estimates
        for estimate in recent_estimates:
            # Try different fields for sales rep ID
            rep_id = (estimate.get('soldById') or 
                     estimate.get('salesRepId') or 
                     estimate.get('employeeId') or 
                     estimate.get('createdById'))
            
            if rep_id and self.lookups:
                rep_name = self.lookups['employees'].get(rep_id, f'Employee {rep_id}')
                
                if rep_name not in sales_performance:
                    sales_performance[rep_name] = {
                        'id': rep_id,
                        'estimates_created': 0,
                        'estimates_sold': 0,
                        'total_estimate_value': 0,
                        'sold_value': 0,
                        'leads_handled': 0,
                        'leads_converted': 0
                    }
                
                sales_performance[rep_name]['estimates_created'] += 1
                sales_performance[rep_name]['total_estimate_value'] += estimate.get('total', 0)
                
                if estimate.get('status', '').lower() in ['sold', 'converted', 'won']:
                    sales_performance[rep_name]['estimates_sold'] += 1
                    sales_performance[rep_name]['sold_value'] += estimate.get('total', 0)
        
        # Process leads
        for lead in recent_leads:
            rep_id = lead.get('employeeId') or lead.get('createdById')
            
            if rep_id and self.lookups and rep_id in self.lookups['employees']:
                rep_name = self.lookups['employees'][rep_id]
                
                if rep_name not in sales_performance:
                    sales_performance[rep_name] = {
                        'id': rep_id,
                        'estimates_created': 0,
                        'estimates_sold': 0,
                        'total_estimate_value': 0,
                        'sold_value': 0,
                        'leads_handled': 0,
                        'leads_converted': 0
                    }
                
                sales_performance[rep_name]['leads_handled'] += 1
                
                if lead.get('status', '').lower() in ['won', 'converted']:
                    sales_performance[rep_name]['leads_converted'] += 1
        
        # Calculate metrics
        for rep_data in sales_performance.values():
            if rep_data['estimates_created'] > 0:
                rep_data['close_rate'] = rep_data['estimates_sold'] / rep_data['estimates_created'] * 100
                rep_data['avg_estimate_value'] = rep_data['total_estimate_value'] / rep_data['estimates_created']
            else:
                rep_data['close_rate'] = 0
                rep_data['avg_estimate_value'] = 0
            
            if rep_data['leads_handled'] > 0:
                rep_data['lead_conversion_rate'] = rep_data['leads_converted'] / rep_data['leads_handled'] * 100
            else:
                rep_data['lead_conversion_rate'] = 0
        
        return sales_performance
    
    def analyze_business_unit_performance(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze performance by business unit.
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing business unit metrics
        """
        print(f"\n=== BUSINESS UNIT PERFORMANCE ({days_back} days) ===")
        
        # Get date range
        start_date, end_date = calculate_date_range(days_back)
        
        # Load reference data if not loaded
        if not self.lookups:
            self.load_reference_data()
        
        # Get jobs and invoices
        print("Fetching jobs and invoices...")
        jobs = self.api.jobs.get_batch().data
        invoices = self.api.invoices.get_batch().data
        estimates = self.api.estimates.get_batch().data
        
        # Filter by date
        recent_jobs = filter_by_date(jobs, 'createdOn', start_date, end_date)
        recent_invoices = filter_by_date(invoices, 'createdOn', start_date, end_date)
        recent_estimates = filter_by_date(estimates, 'createdOn', start_date, end_date)
        
        # Analyze by business unit
        bu_performance = {}
        
        for job in recent_jobs:
            bu_id = job.get('businessUnitId')
            if bu_id and self.lookups:
                bu_name = self.lookups['business_units'].get(bu_id, f'BU {bu_id}')
                
                if bu_name not in bu_performance:
                    bu_performance[bu_name] = {
                        'id': bu_id,
                        'job_count': 0,
                        'completed_jobs': 0,
                        'estimate_count': 0,
                        'revenue': 0,
                        'outstanding': 0
                    }
                
                bu_performance[bu_name]['job_count'] += 1
                
                if job.get('status', '').lower() in ['completed', 'done']:
                    bu_performance[bu_name]['completed_jobs'] += 1
        
        # Add invoice data
        for invoice in recent_invoices:
            bu_id = invoice.get('businessUnitId')
            if bu_id and self.lookups:
                bu_name = self.lookups['business_units'].get(bu_id, f'BU {bu_id}')
                
                if bu_name not in bu_performance:
                    bu_performance[bu_name] = {
                        'id': bu_id,
                        'job_count': 0,
                        'completed_jobs': 0,
                        'estimate_count': 0,
                        'revenue': 0,
                        'outstanding': 0
                    }
                
                bu_performance[bu_name]['revenue'] += invoice.get('total', 0)
                bu_performance[bu_name]['outstanding'] += invoice.get('balance', 0)
        
        # Add estimate data
        for estimate in recent_estimates:
            bu_id = estimate.get('businessUnitId')
            if bu_id and self.lookups:
                bu_name = self.lookups['business_units'].get(bu_id, f'BU {bu_id}')
                
                if bu_name in bu_performance:
                    bu_performance[bu_name]['estimate_count'] += 1
        
        # Calculate metrics
        for bu_data in bu_performance.values():
            if bu_data['job_count'] > 0:
                bu_data['completion_rate'] = bu_data['completed_jobs'] / bu_data['job_count'] * 100
                bu_data['avg_job_value'] = bu_data['revenue'] / bu_data['job_count']
            else:
                bu_data['completion_rate'] = 0
                bu_data['avg_job_value'] = 0
            
            if bu_data['revenue'] > 0:
                bu_data['collection_rate'] = (bu_data['revenue'] - bu_data['outstanding']) / bu_data['revenue'] * 100
            else:
                bu_data['collection_rate'] = 0
        
        return bu_performance
    
    def generate_performance_report(self, days_back: int = 30, export: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Args:
            days_back: Number of days to analyze
            export: Whether to export to CSV
            
        Returns:
            Complete performance analysis
        """
        print(f"\n{'='*60}")
        print(f"PERFORMANCE REPORT - Last {days_back} Days")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Get all performance metrics
        tech_performance = self.analyze_technician_performance(days_back)
        sales_performance = self.analyze_sales_performance(days_back)
        bu_performance = self.analyze_business_unit_performance(days_back)
        
        # Sort and display top performers
        
        # Top Technicians by Revenue
        print("\n🔧 TOP TECHNICIANS BY REVENUE:")
        print("-" * 60)
        sorted_techs = sorted(
            tech_performance.items(),
            key=lambda x: x[1]['revenue_generated'],
            reverse=True
        )
        
        for i, (tech_name, metrics) in enumerate(sorted_techs[:10], 1):
            print(f"\n{i}. {tech_name}")
            print(f"   Revenue Generated: ${metrics['revenue_generated']:,.2f}")
            print(f"   Appointments: {metrics['appointments']} ({metrics['completion_rate']:.1f}% completed)")
            print(f"   Hours Worked: {metrics['total_hours']:.1f}")
            print(f"   Revenue/Hour: ${metrics['revenue_per_hour']:,.2f}")
        
        # Top Sales Reps by Value Sold
        print("\n💼 TOP SALES REPS BY VALUE SOLD:")
        print("-" * 60)
        sorted_sales = sorted(
            sales_performance.items(),
            key=lambda x: x[1]['sold_value'],
            reverse=True
        )
        
        for i, (rep_name, metrics) in enumerate(sorted_sales[:10], 1):
            print(f"\n{i}. {rep_name}")
            print(f"   Value Sold: ${metrics['sold_value']:,.2f}")
            print(f"   Estimates: {metrics['estimates_created']} ({metrics['close_rate']:.1f}% closed)")
            print(f"   Avg Estimate: ${metrics['avg_estimate_value']:,.2f}")
            print(f"   Leads: {metrics['leads_handled']} ({metrics['lead_conversion_rate']:.1f}% converted)")
        
        # Business Unit Performance
        print("\n🏢 BUSINESS UNIT PERFORMANCE:")
        print("-" * 60)
        sorted_bus = sorted(
            bu_performance.items(),
            key=lambda x: x[1]['revenue'],
            reverse=True
        )
        
        for bu_name, metrics in sorted_bus:
            print(f"\n{bu_name}")
            print(f"   Revenue: ${metrics['revenue']:,.2f}")
            print(f"   Jobs: {metrics['job_count']} ({metrics['completion_rate']:.1f}% completed)")
            print(f"   Avg Job Value: ${metrics['avg_job_value']:,.2f}")
            print(f"   Collection Rate: {metrics['collection_rate']:.1f}%")
        
        # Export to CSV if requested
        if export:
            # Export technician performance
            tech_export = []
            for name, metrics in tech_performance.items():
                tech_export.append({
                    'Name': name,
                    'Appointments': metrics['appointments'],
                    'Completed': metrics['completed'],
                    'Completion_Rate': metrics['completion_rate'],
                    'Hours_Worked': metrics['total_hours'],
                    'Revenue_Generated': metrics['revenue_generated'],
                    'Revenue_Per_Hour': metrics['revenue_per_hour']
                })
            
            tech_filename = f"technician_performance_{datetime.now().strftime('%Y%m%d')}.csv"
            export_to_csv(tech_export, tech_filename)
            print(f"\n📁 Technician report exported to: {tech_filename}")
            
            # Export sales performance
            sales_export = []
            for name, metrics in sales_performance.items():
                sales_export.append({
                    'Name': name,
                    'Estimates_Created': metrics['estimates_created'],
                    'Estimates_Sold': metrics['estimates_sold'],
                    'Close_Rate': metrics['close_rate'],
                    'Total_Value': metrics['total_estimate_value'],
                    'Sold_Value': metrics['sold_value'],
                    'Leads_Handled': metrics['leads_handled'],
                    'Lead_Conversion_Rate': metrics['lead_conversion_rate']
                })
            
            sales_filename = f"sales_performance_{datetime.now().strftime('%Y%m%d')}.csv"
            export_to_csv(sales_export, sales_filename)
            print(f"📁 Sales report exported to: {sales_filename}")
            
            # Export business unit performance
            bu_export = []
            for name, metrics in bu_performance.items():
                bu_export.append({
                    'Business_Unit': name,
                    'Jobs': metrics['job_count'],
                    'Completed_Jobs': metrics['completed_jobs'],
                    'Completion_Rate': metrics['completion_rate'],
                    'Revenue': metrics['revenue'],
                    'Avg_Job_Value': metrics['avg_job_value'],
                    'Collection_Rate': metrics['collection_rate']
                })
            
            bu_filename = f"business_unit_performance_{datetime.now().strftime('%Y%m%d')}.csv"
            export_to_csv(bu_export, bu_filename)
            print(f"📁 Business unit report exported to: {bu_filename}")
        
        return {
            'technicians': tech_performance,
            'sales': sales_performance,
            'business_units': bu_performance
        }


def main():
    """Run performance analysis."""
    # Initialize reporter
    reporter = PerformanceReporter()
    
    # Generate reports for different time periods
    periods = [7, 30, 90]
    
    for days in periods:
        print(f"\n{'='*60}")
        print(f"Analyzing {days}-day performance...")
        report = reporter.generate_performance_report(days_back=days, export=(days == 30))
        
        # Save summary to JSON
        summary_file = f"performance_summary_{days}days.json"
        with open(summary_file, 'w') as f:
            # Create summary statistics
            summary = {
                'period_days': days,
                'generated': datetime.now().isoformat(),
                'top_technician': max(report['technicians'].items(), 
                                     key=lambda x: x[1]['revenue_generated'])[0] if report['technicians'] else None,
                'top_sales_rep': max(report['sales'].items(), 
                                    key=lambda x: x[1]['sold_value'])[0] if report['sales'] else None,
                'top_business_unit': max(report['business_units'].items(), 
                                        key=lambda x: x[1]['revenue'])[0] if report['business_units'] else None,
                'total_revenue': sum(bu['revenue'] for bu in report['business_units'].values())
            }
            json.dump(summary, f, indent=2, default=str)
        print(f"📊 Summary saved to: {summary_file}")


if __name__ == "__main__":
    main()