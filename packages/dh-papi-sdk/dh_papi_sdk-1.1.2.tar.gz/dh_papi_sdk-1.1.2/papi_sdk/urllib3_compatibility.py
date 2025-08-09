"""
Simple urllib3 Compatibility Patch for OpenAPI Generated Clients

This module provides a simple patch that filters out problematic parameters 
before they reach urllib3.PoolManager.
"""

def apply_urllib3_patch():
    """
    Apply a simple patch that filters out ca_cert_data from urllib3.PoolManager calls.
    """
    try:
        import urllib3
        
        # Check if already patched
        if hasattr(urllib3.PoolManager, '_ca_cert_data_patched'):
            print("✅ urllib3 PoolManager already patched")
            return
        
        # Store the original PoolManager.__init__ method
        original_pool_init = urllib3.PoolManager.__init__
        
        def patched_pool_init(self, *args, **kwargs):
            """
            Patched PoolManager.__init__ that filters out problematic ca_cert_data parameter
            """
            # Remove the problematic parameter before calling urllib3
            if 'ca_cert_data' in kwargs:
                print(f"🔧 Filtering out ca_cert_data parameter (value: {kwargs['ca_cert_data']})")
                del kwargs['ca_cert_data']
            
            # Call the original __init__ with filtered parameters
            return original_pool_init(self, *args, **kwargs)
        
        # Apply the patch
        urllib3.PoolManager.__init__ = patched_pool_init
        urllib3.PoolManager._ca_cert_data_patched = True
        
        print("✅ urllib3 PoolManager patched successfully (ca_cert_data filtering)")
        
    except ImportError as e:
        print(f"⚠️  Could not import urllib3 for patching: {e}")
    except Exception as e:
        print(f"❌ Error patching urllib3: {e}")
        import traceback
        traceback.print_exc()


def apply_proxy_manager_patch():
    """
    Apply the same patch to ProxyManager
    """
    try:
        import urllib3
        
        # Check if already patched
        if hasattr(urllib3.ProxyManager, '_ca_cert_data_patched'):
            return
        
        # Store the original ProxyManager.__init__ method
        original_proxy_init = urllib3.ProxyManager.__init__
        
        def patched_proxy_init(self, *args, **kwargs):
            """
            Patched ProxyManager.__init__ that filters out problematic ca_cert_data parameter
            """
            # Remove the problematic parameter before calling urllib3
            if 'ca_cert_data' in kwargs:
                print(f"🔧 Filtering out ca_cert_data parameter from ProxyManager")
                del kwargs['ca_cert_data']
            
            # Call the original __init__ with filtered parameters
            return original_proxy_init(self, *args, **kwargs)
        
        # Apply the patch
        urllib3.ProxyManager.__init__ = patched_proxy_init
        urllib3.ProxyManager._ca_cert_data_patched = True
        
        print("✅ urllib3 ProxyManager patched successfully")
        
    except Exception as e:
        print(f"❌ Error patching ProxyManager: {e}")


def apply_socks_proxy_patch():
    """
    Apply the same patch to SOCKSProxyManager if available
    """
    try:
        from urllib3.contrib.socks import SOCKSProxyManager
        
        # Check if already patched
        if hasattr(SOCKSProxyManager, '_ca_cert_data_patched'):
            return
        
        # Store the original SOCKSProxyManager.__init__ method
        original_socks_init = SOCKSProxyManager.__init__
        
        def patched_socks_init(self, *args, **kwargs):
            """
            Patched SOCKSProxyManager.__init__ that filters out problematic ca_cert_data parameter
            """
            # Remove the problematic parameter before calling urllib3
            if 'ca_cert_data' in kwargs:
                print(f"🔧 Filtering out ca_cert_data parameter from SOCKSProxyManager")
                del kwargs['ca_cert_data']
            
            # Call the original __init__ with filtered parameters
            return original_socks_init(self, *args, **kwargs)
        
        # Apply the patch
        SOCKSProxyManager.__init__ = patched_socks_init
        SOCKSProxyManager._ca_cert_data_patched = True
        
        print("✅ urllib3 SOCKSProxyManager patched successfully")
        
    except ImportError:
        # SOCKSProxyManager not available, skip
        pass
    except Exception as e:
        print(f"❌ Error patching SOCKSProxyManager: {e}")


def apply_all_patches():
    """
    Apply all urllib3 compatibility patches
    """
    print("🔧 Applying urllib3 compatibility patches...")
    apply_urllib3_patch()
    apply_proxy_manager_patch()
    apply_socks_proxy_patch()
    print("✅ urllib3 compatibility patches complete")
