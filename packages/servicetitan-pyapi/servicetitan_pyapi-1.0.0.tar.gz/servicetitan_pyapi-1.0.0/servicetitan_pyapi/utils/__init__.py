# servicetitan_pyapi/utils/__init__.py
"""
Utility functions for the ServiceTitan API client.
"""

from .exceptions import (
    ServiceTitanError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError
)

from .helpers import (
    parse_datetime,
    format_datetime,
    calculate_date_range,
    chunk_list,
    retry_with_backoff,
    export_to_csv,
    create_lookup_dict,
    filter_by_date,
    calculate_metrics
)

__all__ = [
    # Exceptions
    'ServiceTitanError',
    'AuthenticationError',
    'RateLimitError',
    'NotFoundError',
    'ValidationError',
    'ServerError',
    # Helpers
    'parse_datetime',
    'format_datetime',
    'calculate_date_range',
    'chunk_list',
    'retry_with_backoff',
    'export_to_csv',
    'create_lookup_dict',
    'filter_by_date',
    'calculate_metrics'
]