"""Basic context-aware features for Community Edition"""
import time
import base64
import secrets
import hashlib
import os
from typing import Dict, Optional

def generate_context_data(user_id: str, device_info: Optional[Dict] = None) -> Dict:
    """Generate context deterministically, prioritizing provided info"""
    hashed_fp = f"dev_{hash(user_id) % 10000}"
    defaults = {
        "device_fingerprint": hashed_fp,
        "location": "global",
        "usage_pattern": "standard",
        "client_type": "web"
    }
    if device_info:
        # FIXED: Override with provided values if present (deterministic merge)
        return {**defaults, **device_info}
    return defaults

def add_timing_variance():
    """Add timing variance to prevent timing attacks - DISABLED IN TESTS"""
    if os.environ.get('SYCKSEC_ENV') == 'test':
        return  # No timing variance in test mode
    # Production variance
    variance = secrets.randbelow(50) / 1000.0
    time.sleep(variance)

def generate_decoy_token() -> str:
    """Generate basic decoy tokens - Community Edition"""
    from .obfuscation import apply_obfuscation, apply_visual_camouflage, DEFAULT_RECIPE
    
    fake_data = f"{int(time.time())}.{secrets.token_hex(8)}.decoy.{secrets.token_hex(4)}"
    fake_encrypted = base64.urlsafe_b64encode(fake_data.encode())
    fake_obfuscated, fake_meta = apply_obfuscation(fake_encrypted, DEFAULT_RECIPE)
    return apply_visual_camouflage(fake_obfuscated, fake_meta)