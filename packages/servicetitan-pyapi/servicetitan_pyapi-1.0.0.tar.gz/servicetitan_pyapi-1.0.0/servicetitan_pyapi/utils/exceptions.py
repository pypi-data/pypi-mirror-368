# servicetitan_pyapi/utils/exceptions.py
"""
Custom exceptions for ServiceTitan API client.
"""

from typing import Optional, Dict, Any


class ServiceTitanError(Exception):
    """Base exception for ServiceTitan API errors"""
    
    def __init__(self, message: str, response: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.response = response
        self.error_code = None
        self.request_id = None
        
        if response:
            self.error_code = response.get('errorCode')
            self.request_id = response.get('requestId')
    
    def __str__(self):
        if self.error_code:
            return f"{self.message} (Error Code: {self.error_code})"
        return self.message


class AuthenticationError(ServiceTitanError):
    """Raised when authentication fails"""
    pass


class RateLimitError(ServiceTitanError):
    """Raised when API rate limit is exceeded"""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        super().__init__(message, response)
        self.retry_after = retry_after


class NotFoundError(ServiceTitanError):
    """Raised when requested resource is not found"""
    pass


class ValidationError(ServiceTitanError):
    """Raised when request validation fails"""
    
    def __init__(self, message: str, validation_errors: Optional[Dict[str, Any]] = None, response: Optional[Dict[str, Any]] = None):
        super().__init__(message, response)
        self.validation_errors = validation_errors


class ServerError(ServiceTitanError):
    """Raised when server returns 5xx error"""
    pass
