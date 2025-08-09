"""
PAPI SDK - Platform API Python SDK

A Python SDK for accessing Delivery Hero's Salesforce Platform API.
"""

__version__ = "1.1.2"

# ============================================================================
# Apply urllib3 compatibility patches FIRST
# ============================================================================
try:
    from .urllib3_compatibility import apply_all_patches
    apply_all_patches()
except ImportError:
    print("⚠️  urllib3 compatibility patches not available")
except Exception as e:
    print(f"⚠️  Error applying urllib3 patches: {e}")

# ============================================================================
# Import main components
# ============================================================================
from .client import Client
from .auth import AuthClient  
from .vrm_bulk_client import BulkAPI

# ============================================================================
# Public API
# ============================================================================
__all__ = [
    "PapiSdk",           # Main interface (alias)
    "Client",            # Full class name
    "BulkAPI",           # Direct access
    "AuthClient",        # Direct access
    "__version__",
]

# Convenience alias for easier imports
PapiSdk = Client

print(f"🚀 DH PAPI SDK v{__version__} initialized")
