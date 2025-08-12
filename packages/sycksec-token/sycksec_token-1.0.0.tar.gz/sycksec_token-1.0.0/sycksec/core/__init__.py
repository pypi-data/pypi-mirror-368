# core/__init__.py - Initialization for SyckSec core package

# Import key components for easy access
from .token_engine import SyckSecTokenEngine
from .crypto_utils import encrypt_data, decrypt_data, sign_token, verify_signature
from .obfuscation import (
    apply_obfuscation, remove_obfuscation,
    apply_visual_camouflage, remove_visual_camouflage,
    cached_pattern_for_user, validate_recipe
)
from .context import generate_context_data, add_timing_variance

# Optional: Package-level constants or setup
__version__ = "1.0.0"  # Example: Add a version string

# Explicitly define what to export (for 'from sycksec.core import *')
__all__ = [
    'SyckSecTokenEngine',
    'encrypt_data', 'decrypt_data', 'sign_token', 'verify_signature',
    'apply_obfuscation', 'remove_obfuscation', 'apply_visual_camouflage', 'remove_visual_camouflage',
    'cached_pattern_for_user', 'validate_recipe',
    'generate_context_data', 'add_timing_variance'
]
