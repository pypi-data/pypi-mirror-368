"""
SyckSec Community Edition - Next-Generation Token System
A modern, secure token system with advanced obfuscation and anti-analysis features.
"""

__version__ = "1.0.0rc1"  # Changed from "1.0.0-community"
__author__ = "SyckSec Team"
__email__ = "community@sycksec.com"
__license__ = "MIT"

from .core.token_engine import SyckSecTokenEngine
from .config import SyckSecConfig
from .utils.exceptions import *

class SyckSec:
    """
    SyckSec Community Edition - Open Source Token System
    
    Provides enterprise-grade token security with:
    - AES-256 encryption (1-2 layers)
    - Dynamic obfuscation patterns
    - UUID-like camouflage
    - Basic context-aware features
    """
    
    def __init__(self, config: 'SyckSecConfig' = None):
        self.config = config or SyckSecConfig()
        self.engine = SyckSecTokenEngine(self.config)
    
    def generate(self, user_id: str, **kwargs) -> str:
        """Generate a secure token for the given user"""
        return self.engine.generate_token(user_id, **kwargs)
    
    def verify(self, token: str, user_id: str, **kwargs) -> dict:
        """Verify and decode a secure token"""
        return self.engine.verify_token(token, user_id, **kwargs)
    
    def refresh(self, token: str, user_id: str, threshold_seconds: int = 300) -> str:
        """Auto-refresh token if expiring soon"""
        return self.engine.refresh_token_if_needed(token, user_id, threshold_seconds)
    
    def refresh_token_if_needed(self, *args, **kwargs):
        return self.engine.refresh_token_if_needed(*args, **kwargs)
    
    def generate_batch(self, requests: list, max_batch_size: int = 50) -> list:
        """Generate multiple tokens efficiently (Community: max 50)"""
        if len(requests) > max_batch_size:
            raise ValueError(f"Community Edition batch size limited to {max_batch_size}")
        return self.engine.generate_tokens_batch(requests)
    
    def verify_batch(self, requests: list, max_batch_size: int = 50) -> list:
        """Verify multiple tokens efficiently (Community: max 50)"""
        if len(requests) > max_batch_size:
            raise ValueError(f"Community Edition batch size limited to {max_batch_size}")
        return self.engine.verify_tokens_batch(requests)

def create_client(master_secret: str = None, **config_kwargs) -> SyckSec:
    """Create a SyckSec client with minimal configuration"""
    config_dict = config_kwargs.copy()
    if master_secret:
        config_dict['master_secret'] = master_secret
    
    config = SyckSecConfig(**config_dict)
    return SyckSec(config)

# Export main classes and functions
__all__ = [
    'SyckSec',
    'SyckSecConfig', 
    'SyckSecTokenEngine',
    'create_client',
    'SyckSecError',
    'TokenGenerationError',
    'TokenValidationError',
    'ConfigurationError'
]
