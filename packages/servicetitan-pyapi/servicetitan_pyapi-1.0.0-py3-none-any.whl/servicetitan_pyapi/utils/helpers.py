# servicetitan_pyapi/utils/helpers.py
"""
Helper functions for ServiceTitan API client.
"""

import csv
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable, TypeVar, Union
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


def parse_datetime(date_string: Optional[str]) -> Optional[datetime]:
    """
    Parse ServiceTitan datetime string to Python datetime object.
    
    Args:
        date_string: ISO format datetime string
    
    Returns:
        datetime object or None if input is None/invalid
    """
    if not date_string:
        return None
    
    try:
        # Handle different datetime formats
        if 'T' in date_string:
            # ISO format with time
            if date_string.endswith('Z'):
                return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return datetime.fromisoformat(date_string)
        else:
            # Date only
            return datetime.strptime(date_string, '%Y-%m-%d')
    except (ValueError, AttributeError) as e:
        logger.warning(f"Could not parse datetime: {date_string} - {e}")
        return None


def format_datetime(dt: Optional[datetime], include_time: bool = True) -> Optional[str]:
    """
    Format datetime object to ServiceTitan API format.
    
    Args:
        dt: datetime object
        include_time: Whether to include time in the output
    
    Returns:
        ISO format datetime string or None
    """
    if not dt:
        return None
    
    if include_time:
        return dt.isoformat()
    return dt.date().isoformat()


def calculate_date_range(
    days_back: int = 30,
    end_date: Optional[datetime] = None
) -> tuple[datetime, datetime]:
    """
    Calculate a date range for API queries.
    
    Args:
        days_back: Number of days to go back
        end_date: End date (defaults to now)
    
    Returns:
        Tuple of (start_date, end_date)
    """
    if end_date is None:
        end_date = datetime.now()
    
    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date


def chunk_list(items: List[T], chunk_size: int = 100) -> List[List[T]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List of chunks
    """
    chunks = []
    for i in range(0, len(items), chunk_size):
        chunks.append(items[i:i + chunk_size])
    return chunks


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry function calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = base_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {delay} seconds..."
                        )
                        time.sleep(delay)
                        delay *= exponential_base
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
                        raise
            
            raise last_exception
        
        return wrapper
    return decorator


def export_to_csv(
    data: List[Dict[str, Any]],
    filename: str,
    fieldnames: Optional[List[str]] = None
) -> None:
    """
    Export data to CSV file.
    
    Args:
        data: List of dictionaries to export
        filename: Output filename
        fieldnames: Optional list of field names (uses all keys if not provided)
    """
    if not data:
        logger.warning(f"No data to export to {filename}")
        return
    
    # Determine fieldnames if not provided
    if fieldnames is None:
        fieldnames = set()
        for record in data:
            fieldnames.update(record.keys())
        fieldnames = sorted(list(fieldnames))
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    logger.info(f"Exported {len(data)} records to {filename}")


def create_lookup_dict(
    items: List[Dict[str, Any]],
    key_field: str = 'id',
    value_field: Optional[str] = None
) -> Dict[Any, Any]:
    """
    Create a lookup dictionary from a list of items.
    
    Args:
        items: List of dictionaries
        key_field: Field to use as dictionary key
        value_field: Field to use as value (uses entire dict if None)
    
    Returns:
        Lookup dictionary
    """
    lookup = {}
    
    for item in items:
        key = item.get(key_field)
        if key is None:
            continue
        
        if value_field:
            lookup[key] = item.get(value_field)
        else:
            lookup[key] = item
    
    return lookup


def filter_by_date(
    items: List[Dict[str, Any]],
    date_field: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Filter items by date range.
    
    Args:
        items: List of items to filter
        date_field: Name of the date field to filter on
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
    
    Returns:
        Filtered list of items
    """
    filtered = []
    
    for item in items:
        date_str = item.get(date_field)
        if not date_str:
            continue
        
        item_date = parse_datetime(date_str)
        if not item_date:
            continue
        
        if start_date and item_date < start_date:
            continue
        
        if end_date and item_date > end_date:
            continue
        
        filtered.append(item)
    
    return filtered


def calculate_metrics(
    items: List[Dict[str, Any]],
    group_by: Optional[str] = None,
    sum_fields: Optional[List[str]] = None,
    count_field: Optional[str] = None,
    avg_fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Calculate metrics from a list of items.
    
    Args:
        items: List of items to analyze
        group_by: Optional field to group by
        sum_fields: Fields to sum
        count_field: Field to count occurrences
        avg_fields: Fields to average
    
    Returns:
        Dictionary of calculated metrics
    """
    metrics = {}
    
    if not items:
        return metrics
    
    if group_by:
        # Group items
        groups = {}
        for item in items:
            key = item.get(group_by)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        
        # Calculate metrics per group
        for key, group_items in groups.items():
            group_metrics = {
                'count': len(group_items)
            }
            
            if sum_fields:
                for field in sum_fields:
                    total = sum(item.get(field, 0) for item in group_items)
                    group_metrics[f'{field}_sum'] = total
            
            if avg_fields:
                for field in avg_fields:
                    values = [item.get(field, 0) for item in group_items if item.get(field) is not None]
                    if values:
                        group_metrics[f'{field}_avg'] = sum(values) / len(values)
            
            metrics[key] = group_metrics
    else:
        # Overall metrics
        metrics['count'] = len(items)
        
        if sum_fields:
            for field in sum_fields:
                total = sum(item.get(field, 0) for item in items)
                metrics[f'{field}_sum'] = total
        
        if avg_fields:
            for field in avg_fields:
                values = [item.get(field, 0) for item in items if item.get(field) is not None]
                if values:
                    metrics[f'{field}_avg'] = sum(values) / len(values)
        
        if count_field:
            counts = {}
            for item in items:
                value = item.get(count_field)
                counts[value] = counts.get(value, 0) + 1
            metrics[f'{count_field}_counts'] = counts
    
    return metrics


# Additional helper for saving/loading continuation tokens
def save_continuation_tokens(tokens: Dict[str, Optional[str]], filename: str = 'continuation_tokens.json') -> None:
    """
    Save continuation tokens to a JSON file.
    
    Args:
        tokens: Dictionary of continuation tokens
        filename: File to save tokens to
    """
    with open(filename, 'w') as f:
        json.dump(tokens, f, indent=2)
    logger.info(f"Saved continuation tokens to {filename}")


def load_continuation_tokens(filename: str = 'continuation_tokens.json') -> Dict[str, Optional[str]]:
    """
    Load continuation tokens from a JSON file.
    
    Args:
        filename: File to load tokens from
    
    Returns:
        Dictionary of continuation tokens
    """
    try:
        with open(filename, 'r') as f:
            tokens = json.load(f)
        logger.info(f"Loaded continuation tokens from {filename}")
        return tokens
    except FileNotFoundError:
        logger.info(f"No existing token file found at {filename}")
        return {}