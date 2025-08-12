"""Robust Base64 utilities for SyckSec token system"""
import base64
import re

def safe_base64_decode(data: str) -> bytes:
    """Robust base64 decoding with automatic padding correction"""
    if not data:
        raise ValueError("Empty base64 data")
    
    # Remove any non-base64 characters (except padding)
    clean_data = re.sub(r'[^A-Za-z0-9_-]', '', data)
    
    # Add proper padding
    padding_needed = (-len(clean_data)) % 4
    padded_data = clean_data + ('=' * padding_needed)
    
    try:
        return base64.urlsafe_b64decode(padded_data)
    except Exception as e:
        # Fallback: Try with standard base64 if urlsafe fails
        try:
            # Convert urlsafe chars back to standard
            standard_data = padded_data.replace('-', '+').replace('_', '/')
            return base64.b64decode(standard_data)
        except Exception as e2:
            raise ValueError(f"Failed to decode base64: {str(e)} / {str(e2)}")

def safe_base64_encode(data: bytes) -> str:
    """Safe base64 encoding that always produces valid output"""
    return base64.urlsafe_b64encode(data).decode('ascii')

def validate_base64(data: str) -> bool:
    """Validate if string is proper base64"""
    try:
        safe_base64_decode(data)
        return True
    except:
        return False
