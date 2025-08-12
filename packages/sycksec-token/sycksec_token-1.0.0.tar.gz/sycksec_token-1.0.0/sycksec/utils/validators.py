"""Input validation utilities"""
import re
from ..security.profiles import SECURITY_PROFILES
from .exceptions import SecurityProfileError

def validate_user_id(user_id: str) -> bool:
    """Validate user ID format"""
    if not user_id or not isinstance(user_id, str):
        return False
    
    if len(user_id) == 0 or len(user_id) > 255:
        return False
    
    # Allow alphanumeric, hyphens, underscores, periods, and @ for email-like IDs
    import re
    pattern = r'^[a-zA-Z0-9_.-@]+$'
    return bool(re.match(pattern, user_id))

def validate_ttl(ttl: int, security_profile: str = "standard") -> bool:
    """Validate TTL against security profile"""
    if not isinstance(ttl, int) or ttl <= 0:
        return False
    
    profile = SECURITY_PROFILES.get(security_profile)
    if not profile:
        return False
    
    return profile["min_ttl"] <= ttl <= profile["max_ttl"]

def validate_security_profile(security_profile: str) -> bool:
    """Validate security profile exists"""
    return security_profile in SECURITY_PROFILES

def validate_device_info(device_info: dict) -> bool:
    """Validate device info structure"""
    if not isinstance(device_info, dict):
        return False
    
    allowed_keys = {"fingerprint", "location", "pattern", "client_type"}
    return all(key in allowed_keys for key in device_info.keys())
