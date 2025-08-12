"""Security profiles for SyckSec Community Edition"""

# Community Edition: Single Standard Profile
SECURITY_PROFILES = {
    "standard": {
        "layers": 2,  # Community max: 2 layers
        "noise_variance": 3,
        "encryption": "AES-256",
        "min_ttl": 300,
        "max_ttl": 3600
    }
}

# Note: Enterprise profiles (performance, high_value) available in paid version
