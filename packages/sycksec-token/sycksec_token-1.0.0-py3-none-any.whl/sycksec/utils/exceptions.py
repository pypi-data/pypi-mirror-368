"""Custom exceptions for SyckSec"""
import time
from typing import Dict, Optional

class SyckSecError(Exception):
    """Base exception for SyckSec library"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = time.time()

class TokenGenerationError(SyckSecError):
    """Token generation failed"""
    pass

class TokenValidationError(SyckSecError):
    """Token validation failed"""
    pass

class RateLimitExceededError(SyckSecError):
    """Rate limit exceeded"""
    pass

class ConfigurationError(SyckSecError):
    """Configuration error"""
    pass

class SecurityProfileError(SyckSecError):
    """Security profile error"""
    pass
