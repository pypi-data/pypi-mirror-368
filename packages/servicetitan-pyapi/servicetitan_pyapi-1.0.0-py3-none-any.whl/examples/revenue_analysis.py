#!/usr/bin/env python3
"""
revenue_analysis.py - Revenue Analysis and Forecasting

Demonstrates how to analyze revenue patterns, track collections,
and forecast future revenue using ServiceTitan data.
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
from typing import Dict, List, Any, Optional, Tuple
import json
import statistics


class RevenueAnalyzer:
    """Analyze revenue patterns and forecast future performance."""
    
    def __init__(self, config_path: str = "config/servicetitan_config.json"):
        """Initialize the analyzer with ServiceTitan API."""
        self.api = ServiceTitanAPI(config_path)
        self.lookups = None
        
    def load_reference_data(self):
        """Load reference data for analysis."""
        print("Loading reference data...")
        self.lookups = self.api.settings.create_lookup_tables()
        return self.lookups
    
    def analyze_revenue_by_period(self, days_back: int = 90) -> Dict[str, Any]:
        """
        Analyze revenue patterns over time periods.
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing period-based revenue metrics
        """
        print(f"\n=== REVENUE ANALYSIS ({days_back} days) ===")
        
        # Get date range
        start_date, end_date = calculate_date_range(days_back)
        
        # Get invoices
        print("Fetching invoices...")
        invoices = self.api.invoices.get_batch().data
        
        # Filter by date
        recent_invoices = filter_by_date(invoices, 'createdOn', start_date, end_date)
        
        # Organize by period
        daily_revenue = {}
        weekly_revenue = {}
        monthly_revenue = {}
        
        for invoice in recent_invoices:
            created = parse_datetime(invoice.get('createdOn'))
            if not created:
                continue
            
            total = invoice.get('total', 0)
            paid = total - invoice.get('balance', 0)
            
            # Daily
            day_key = created.date().isoformat()
            if day_key not in daily_revenue:
                daily_revenue[day_key] = {'total': 0, 'paid': 0, 'count': 0}
            daily_revenue[day_key]['total'] += total
            daily_revenue[day_key]['paid'] += paid
            daily_revenue[day_key]['count'] += 1
            
            # Weekly
            week_key = created.strftime('%Y-W%U')
            if week_key not in weekly_revenue:
                weekly_revenue[week_key] = {'total': 0, 'paid': 0, 'count': 0}
            weekly_revenue[week_key]['total'] += total
            weekly_revenue[week_key]['paid'] += paid
            weekly_revenue[week_key]['count'] += 1
            
            # Monthly
            month_key = created.strftime('%Y-%m')
            if month_key not in monthly_revenue:
                monthly_revenue[month_key] = {'total': 0, 'paid': 0, 'count': 0}
            monthly_revenue[month_key]['total'] += total
            monthly_revenue[month_key]['paid'] += paid
            monthly_revenue[month_key]['count'] += 1
        
        return {
            'daily': daily_revenue,
            'weekly': weekly_revenue,
            'monthly': monthly_revenue,
            'total_invoices': len(recent_invoices)
        }
    
    def analyze_revenue_by_source(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze revenue by lead source and campaign.
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing source-based revenue metrics
        """
        print(f"\n=== REVENUE BY SOURCE ({days_back} days) ===")
        
        # Get date range
        start_date, end_date = calculate_date_range(days_back)
        
        # Load reference data if not loaded
        if not self.lookups:
            self.load_reference_data()
        
        # Get data
        print("Fetching jobs, invoices, and campaigns...")
        jobs = self.api.jobs.get_batch().data
        invoices = self.api.invoices.get_batch().data
        campaigns = self.api.marketing.get_all_campaigns()
        
        # Filter by date
        recent_jobs = filter_by_date(jobs, 'createdOn', start_date, end_date)
        recent_invoices = filter_by_date(invoices, 'createdOn', start_date, end_date)
        
        # Create job to campaign mapping
        job_campaigns = {}
        for job in recent_jobs:
            if job.get('campaignId'):
                job_campaigns[job['id']] = job['campaignId']
        
        # Create campaign lookup
        campaign_lookup = {c['id']: c['name'] for c in campaigns}
        
        # Analyze revenue by source
        source_revenue = {}
        
        for invoice in recent_invoices:
            job_id = invoice.get('jobId')
            total = invoice.get('total', 0)
            
            if job_id and job_id in job_campaigns:
                campaign_id = job_campaigns[job_id]
                campaign_name = campaign_lookup.get(campaign_id, f'Campaign {campaign_id}')
                
                if campaign_name not in source_revenue:
                    source_revenue[campaign_name] = {
                        'invoice_count': 0,
                        'total_revenue': 0,
                        'paid_revenue': 0,
                        'outstanding': 0
                    }
                
                source_revenue[campaign_name]['invoice_count'] += 1
                source_revenue[campaign_name]['total_revenue'] += total
                source_revenue[campaign_name]['paid_revenue'] += total - invoice.get('balance', 0)
                source_revenue[campaign_name]['outstanding'] += invoice.get('balance', 0)
            else:
                # No campaign attribution
                if 'Direct/Unknown' not in source_revenue:
                    source_revenue['Direct/Unknown'] = {
                        'invoice_count': 0,
                        'total_revenue': 0,
                        'paid_revenue': 0,
                        'outstanding': 0
                    }
                
                source_revenue['Direct/Unknown']['invoice_count'] += 1
                source_revenue['Direct/Unknown']['total_revenue'] += total
                source_revenue['Direct/Unknown']['paid_revenue'] += total - invoice.get('balance', 0)
                source_revenue['Direct/Unknown']['outstanding'] += invoice.get('balance', 0)
        
        # Calculate collection rates
        for source_data in source_revenue.values():
            if source_data['total_revenue'] > 0:
                source_data['collection_rate'] = (source_data['paid_revenue'] / 
                                                 source_data['total_revenue'] * 100)
            else:
                source_data['collection_rate'] = 0
            
            if source_data['invoice_count'] > 0:
                source_data['avg_invoice'] = source_data['total_revenue'] / source_data['invoice_count']
            else:
                source_data['avg_invoice'] = 0
        
        return source_revenue
    
    def analyze_revenue_by_service(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze revenue by business unit and job type.
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing service-based revenue metrics
        """
        print(f"\n=== REVENUE BY SERVICE ({days_back} days) ===")
        
        # Get date range
        start_date, end_date = calculate_date_range(days_back)
        
        # Load reference data if not loaded
        if not self.lookups:
            self.load_reference_data()
        
        # Get invoices
        print("Fetching invoices...")
        invoices = self.api.invoices.get_batch().data
        
        # Filter by date
        recent_invoices = filter_by_date(invoices, 'createdOn', start_date, end_date)
        
        # Analyze by business unit
        bu_revenue = {}
        
        for invoice in recent_invoices:
            bu_id = invoice.get('businessUnitId')
            if bu_id and self.lookups and 'business_units' in self.lookups:
                bu_name = self.lookups['business_units'].get(bu_id, f'BU {bu_id}')
                
                if bu_name not in bu_revenue:
                    bu_revenue[bu_name] = {
                        'invoice_count': 0,
                        'total_revenue': 0,
                        'paid_revenue': 0,
                        'outstanding': 0,
                        'items': []
                    }
                
                total = invoice.get('total', 0)
                bu_revenue[bu_name]['invoice_count'] += 1
                bu_revenue[bu_name]['total_revenue'] += total
                bu_revenue[bu_name]['paid_revenue'] += total - invoice.get('balance', 0)
                bu_revenue[bu_name]['outstanding'] += invoice.get('balance', 0)
                
                # Track invoice items for service analysis
                if 'items' in invoice:
                    bu_revenue[bu_name]['items'].extend(invoice['items'])
        
        # Calculate metrics
        for bu_data in bu_revenue.values():
            if bu_data['total_revenue'] > 0:
                bu_data['collection_rate'] = (bu_data['paid_revenue'] / 
                                             bu_data['total_revenue'] * 100)
            else:
                bu_data['collection_rate'] = 0
            
            if bu_data['invoice_count'] > 0:
                bu_data['avg_invoice'] = bu_data['total_revenue'] / bu_data['invoice_count']
            else:
                bu_data['avg_invoice'] = 0
            
            # Remove items list for cleaner output
            del bu_data['items']
        
        return bu_revenue
    
    def forecast_revenue(self, historical_days: int = 90, forecast_days: int = 30) -> Dict[str, Any]:
        """
        Forecast future revenue based on historical patterns.
        
        Args:
            historical_days: Days of historical data to analyze
            forecast_days: Days to forecast into the future
            
        Returns:
            Revenue forecast
        """
        print(f"\n=== REVENUE FORECAST (Next {forecast_days} days) ===")
        
        # Get historical revenue data
        historical = self.analyze_revenue_by_period(historical_days)
        
        # Calculate daily averages and trends
        daily_values = [data['total'] for data in historical['daily'].values()]
        
        if len(daily_values) < 7:
            print("Insufficient data for forecasting")
            return {}
        
        # Calculate statistics
        avg_daily = statistics.mean(daily_values)
        median_daily = statistics.median(daily_values)
        stdev_daily = statistics.stdev(daily_values) if len(daily_values) > 1 else 0
        
        # Calculate trend (simple linear regression)
        x_values = list(range(len(daily_values)))
        y_values = daily_values
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x ** 2 for x in x_values)
        
        # Calculate slope and intercept
        if (n * sum_x2 - sum_x ** 2) != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            intercept = (sum_y - slope * sum_x) / n
        else:
            slope = 0
            intercept = avg_daily
        
        # Generate forecast
        forecast = {
            'historical_stats': {
                'avg_daily_revenue': avg_daily,
                'median_daily_revenue': median_daily,
                'stdev_daily_revenue': stdev_daily,
                'trend_slope': slope,
                'data_points': len(daily_values)
            },
            'projections': {}
        }
        
        # Project future revenue
        for i in range(forecast_days):
            future_date = datetime.now().date() + timedelta(days=i+1)
            
            # Use trend line for projection
            projected_value = intercept + slope * (len(daily_values) + i)
            
            # Apply bounds (don't go negative or too far from historical)
            projected_value = max(0, projected_value)
            projected_value = min(projected_value, avg_daily * 3)  # Cap at 3x average
            
            forecast['projections'][future_date.isoformat()] = {
                'projected': projected_value,
                'low': max(0, projected_value - stdev_daily),
                'high': projected_value + stdev_daily
            }
        
        # Calculate period totals
        forecast['summary'] = {
            f'next_{forecast_days}_days': {
                'projected': sum(p['projected'] for p in forecast['projections'].values()),
                'low': sum(p['low'] for p in forecast['projections'].values()),
                'high': sum(p['high'] for p in forecast['projections'].values())
            },
            'projected_monthly': avg_daily * 30,
            'projected_annual': avg_daily * 365
        }
        
        return forecast
    
    def generate_revenue_report(self, days_back: int = 30, export: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive revenue report.
        
        Args:
            days_back: Number of days to analyze
            export: Whether to export to CSV
            
        Returns:
            Complete revenue analysis
        """
        print(f"\n{'='*60}")
        print(f"REVENUE ANALYSIS REPORT - Last {days_back} Days")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Get all analyses
        period_analysis = self.analyze_revenue_by_period(days_back)
        source_analysis = self.analyze_revenue_by_source(days_back)
        service_analysis = self.analyze_revenue_by_service(days_back)
        forecast = self.forecast_revenue(historical_days=days_back, forecast_days=30)
        
        # Calculate totals
        total_revenue = sum(d['total'] for d in period_analysis['daily'].values())
        total_paid = sum(d['paid'] for d in period_analysis['daily'].values())
        total_outstanding = total_revenue - total_paid
        
        # Print summary
        print("\n💰 REVENUE SUMMARY:")
        print("-" * 60)
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print(f"Collected: ${total_paid:,.2f}")
        print(f"Outstanding: ${total_outstanding:,.2f}")
        print(f"Collection Rate: {(total_paid/total_revenue*100 if total_revenue > 0 else 0):.1f}%")
        print(f"Total Invoices: {period_analysis['total_invoices']}")
        
        # Monthly breakdown
        print("\n📅 MONTHLY REVENUE:")
        print("-" * 60)
        for month, data in sorted(period_analysis['monthly'].items()):
            collection_rate = data['paid'] / data['total'] * 100 if data['total'] > 0 else 0
            print(f"{month}: ${data['total']:,.2f} ({data['count']} invoices, {collection_rate:.1f}% collected)")
        
        # Top revenue sources
        print("\n🎯 TOP REVENUE SOURCES:")
        print("-" * 60)
        sorted_sources = sorted(
            source_analysis.items(),
            key=lambda x: x[1]['total_revenue'],
            reverse=True
        )
        
        for i, (source, data) in enumerate(sorted_sources[:10], 1):
            print(f"\n{i}. {source}")
            print(f"   Revenue: ${data['total_revenue']:,.2f}")
            print(f"   Invoices: {data['invoice_count']}")
            print(f"   Avg Invoice: ${data['avg_invoice']:,.2f}")
            print(f"   Collection Rate: {data['collection_rate']:.1f}%")
        
        # Business unit performance
        print("\n🏢 REVENUE BY BUSINESS UNIT:")
        print("-" * 60)
        sorted_bus = sorted(
            service_analysis.items(),
            key=lambda x: x[1]['total_revenue'],
            reverse=True
        )
        
        for bu, data in sorted_bus:
            print(f"\n{bu}")
            print(f"   Revenue: ${data['total_revenue']:,.2f}")
            print(f"   Collection Rate: {data['collection_rate']:.1f}%")
            print(f"   Avg Invoice: ${data['avg_invoice']:,.2f}")
        
        # Forecast
        if forecast:
            print("\n🔮 REVENUE FORECAST:")
            print("-" * 60)
            print(f"Based on {forecast['historical_stats']['data_points']} days of data:")
            print(f"Average Daily Revenue: ${forecast['historical_stats']['avg_daily_revenue']:,.2f}")
            print(f"Trend: {'↑ Growing' if forecast['historical_stats']['trend_slope'] > 0 else '↓ Declining'}")
            print(f"\nNext 30 Days Projection:")
            print(f"  Expected: ${forecast['summary']['next_30_days']['projected']:,.2f}")
            print(f"  Range: ${forecast['summary']['next_30_days']['low']:,.2f} - ${forecast['summary']['next_30_days']['high']:,.2f}")
            print(f"\nProjected Monthly: ${forecast['summary']['projected_monthly']:,.2f}")
            print(f"Projected Annual: ${forecast['summary']['projected_annual']:,.2f}")
        
        # Export if requested
        if export:
            # Export daily revenue
            daily_export = []
            for date, data in period_analysis['daily'].items():
                daily_export.append({
                    'Date': date,
                    'Revenue': data['total'],
                    'Collected': data['paid'],
                    'Outstanding': data['total'] - data['paid'],
                    'Invoice_Count': data['count']
                })
            
            filename = f"daily_revenue_{datetime.now().strftime('%Y%m%d')}.csv"
            export_to_csv(daily_export, filename)
            print(f"\n📁 Daily revenue exported to: {filename}")
            
            # Export source analysis
            source_export = []
            for source, data in source_analysis.items():
                source_export.append({
                    'Source': source,
                    'Revenue': data['total_revenue'],
                    'Collected': data['paid_revenue'],
                    'Outstanding': data['outstanding'],
                    'Invoices': data['invoice_count'],
                    'Avg_Invoice': data['avg_invoice'],
                    'Collection_Rate': data['collection_rate']
                })
            
            source_filename = f"revenue_by_source_{datetime.now().strftime('%Y%m%d')}.csv"
            export_to_csv(source_export, source_filename)
            print(f"📁 Source analysis exported to: {source_filename}")
        
        return {
            'period_analysis': period_analysis,
            'source_analysis': source_analysis,
            'service_analysis': service_analysis,
            'forecast': forecast,
            'summary': {
                'total_revenue': total_revenue,
                'total_collected': total_paid,
                'total_outstanding': total_outstanding,
                'collection_rate': (total_paid/total_revenue*100 if total_revenue > 0 else 0)
            }
        }


def main():
    """Run revenue analysis."""
    # Initialize analyzer
    analyzer = RevenueAnalyzer()
    
    # Generate reports for different periods
    periods = [30, 60, 90]
    
    for days in periods:
        print(f"\n{'='*60}")
        print(f"Analyzing {days}-day revenue...")
        report = analyzer.generate_revenue_report(days_back=days, export=(days == 30))
        
        # Save report to JSON
        report_file = f"revenue_report_{days}days.json"
        with open(report_file, 'w') as f:
            # Convert to serializable format
            serializable_report = {
                'period': days,
                'generated': datetime.now().isoformat(),
                'summary': report['summary']
            }
            json.dump(serializable_report, f, indent=2, default=str)
        print(f"📊 Report saved to: {report_file}")


if __name__ == "__main__":
    main()