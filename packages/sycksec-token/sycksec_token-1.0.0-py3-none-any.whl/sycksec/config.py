"""Configuration management for SyckSec Community Edition"""
import os
from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class SyckSecConfig:
    """Community Edition configuration - Essential settings only"""
    
    # Core settings
    master_secret: str = field(default_factory=lambda: os.environ.get('SYCKSEC_SECRET', ''))
    default_ttl: int = 900
    max_ttl: int = 86400
    
    # Community Edition: Single security profile
    security_profile: str = "standard"
    
    # Basic audit logging (no advanced analytics)
    enable_audit_logging: bool = True
    
    # Performance settings (Community limits)
    cache_size: int = 100  # Reduced from enterprise
    max_batch_size: int = 50  # Limited batch operations
    
    # Environment settings
    environment: str = field(default_factory=lambda: os.environ.get('SYCKSEC_ENV', 'production'))
    debug: bool = field(default_factory=lambda: os.environ.get('SYCKSEC_DEBUG', 'false').lower() == 'true')
    
    def __post_init__(self):
        # Only require secret in production mode
        if self.environment == 'production' and not self.master_secret:
            raise ValueError("SYCKSEC_SECRET environment variable is required in production mode")
        
        # Use default test secret if none provided in test/dev mode
        if not self.master_secret:
            self.master_secret = 'sycksec-community-default-secret-32chars!'
        
        if len(self.master_secret) < 32:
            raise ValueError("Master secret must be at least 32 characters")
