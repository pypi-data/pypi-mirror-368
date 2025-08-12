"""Helper utilities"""
import time
from typing import Dict, Any

def format_token_info(payload: Dict[str, Any]) -> str:
    """Format token payload for display"""
    issued_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payload['issued_at']))
    expires_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payload['expires_at']))
    
    return f"""
Token Information:
- User ID: {payload['user_id']}
- Issued: {issued_time}
- Expires: {expires_time}
- Device: {payload.get('device_fingerprint', 'unknown')}
- Location: {payload.get('location', 'unknown')}
- Security Profile: {payload.get('security_profile', 'unknown')}
"""

def calculate_token_strength(security_profile: str, ttl: int) -> str:
    """Calculate token security strength"""
    from ..security.profiles import SECURITY_PROFILES
    
    profile = SECURITY_PROFILES.get(security_profile, SECURITY_PROFILES["standard"])
    
    # Calculate strength based on layers, TTL, and profile
    base_score = profile["layers"] * 20
    ttl_score = min(30, (ttl / 3600) * 10)  # Max 30 points for TTL
    variance_score = profile["noise_variance"] * 5
    
    total_score = base_score + ttl_score + variance_score
    
    if total_score >= 80:
        return "High"
    elif total_score >= 50:
        return "Medium"
    else:
        return "Low"

def get_token_metadata(token: str) -> Dict[str, str]:
    """Extract basic metadata from token format"""
    return {
        "format": "UUID-like with checksum",
        "length": str(len(token)),
        "has_checksum": "Yes" if token.count('.') >= 1 else "No",
        "obfuscated": "Yes"
    }
