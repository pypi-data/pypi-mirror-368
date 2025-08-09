# /sdk/py/papi-sdk/papi_sdk/client.py
"""
Main Platform API Client

This provides a simple, one-stop interface for all Platform API services.
urllib3 compatibility patches are applied globally in __init__.py
"""

from typing import Optional
from .auth import AuthClient
from .vrm_bulk_client import BulkAPI
from .generated.generated.api_client import ApiClient
from .generated.generated.configuration import Configuration


class Client:
    """
    Main Platform API Client
    
    This is the primary interface for accessing all Platform API services.
    It handles authentication and provides access to service-specific clients.
    
    Usage:
        # Simple setup
        client = Client(
            client_id="your-client-id",
            client_secret="your-client-secret",
            environment="stg"  # or "prod", "dev"
        )
        
        # Use any service
        jobs = client.vrm_bulk.get_all_jobs()
        
        # Or access services directly
        job = client.vrm_bulk.create_job("Account", "insert")
    """
    
    # Environment URLs
    ENVIRONMENTS = {
        "prod": "https://platformapi.salesforce.deliveryhero.io",
        "stg": "https://platformapi-stg.salesforce.deliveryhero.io",
        "dev": "https://platformapi-dev.salesforce.deliveryhero.io"
    }
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        environment: str = "prod",
        base_url: Optional[str] = None
    ):
        """
        Initialize the Platform API client
        
        Args:
            client_id: Your Platform API client ID
            client_secret: Your Platform API client secret  
            environment: Environment to use ("prod", "stg", "dev")
            base_url: Custom base URL (overrides environment)
        """
        self.environment = environment
        self.base_url = base_url or self.ENVIRONMENTS.get(environment)
        
        if not self.base_url:
            raise ValueError(f"Unknown environment: {environment}. Use: {list(self.ENVIRONMENTS.keys())}")
        
        # Store credentials
        self.client_id = client_id
        self.client_secret = client_secret
        
        # Set up authentication
        self.auth_client = AuthClient(self.base_url, client_id, client_secret)
        
        # Initialize service clients (lazy loading)
        self._vrm_bulk = None
        
        # Test connection on initialization
        self._test_connection()
    
    def _test_connection(self) -> None:
        """Test the connection and authentication on initialization"""
        try:
            token = self.auth_client.get_token()
            if not token:
                raise Exception("Failed to obtain access token")
        except Exception as e:
            raise Exception(f"Failed to authenticate with Platform API: {e}")
    
    def _get_authenticated_api_client(self) -> ApiClient:
        """Get an authenticated API client for making requests"""
        # Get a fresh token
        token = self.auth_client.get_token()
        
        # Create standard configuration (urllib3 patches applied globally)
        config = Configuration(
            host=self.base_url,
            access_token=token
        )
        
        # Use standard generated API client (patches applied globally)
        return ApiClient(configuration=config)
    
    @property
    def vrm_bulk(self) -> BulkAPI:
        """
        Get the VRM Bulk API client
        
        This client handles bulk operations for Salesforce data:
        - Creating bulk jobs
        - Uploading data
        - Monitoring job status
        - Retrieving results
        
        Returns:
            BulkAPI: Ready-to-use bulk operations client
        """
        if self._vrm_bulk is None:
            api_client = self._get_authenticated_api_client()
            self._vrm_bulk = BulkAPI(api_client)
        return self._vrm_bulk
    
    # Add more service clients as you build them:
    # @property
    # def vrm_std(self) -> VrmStdClient:
    #     """Get the VRM Standard API client"""
    #     if self._vrm_std is None:
    #         api_client = self._get_authenticated_api_client()
    #         self._vrm_std = VrmStdClient(api_client)
    #     return self._vrm_std
    
    def test_connection(self) -> bool:
        """
        Test if the connection and authentication are working
        
        Returns:
            bool: True if connection is working, False otherwise
        """
        try:
            token = self.auth_client.get_token(force_refresh=True)
            return bool(token)
        except Exception:
            return False
    
    def get_token(self) -> str:
        """
        Get the current access token
        
        Returns:
            str: Current valid access token
        """
        return self.auth_client.get_token()
    
    def refresh_token(self) -> str:
        """
        Force refresh the access token
        
        Returns:
            str: New access token
        """
        return self.auth_client.get_token(force_refresh=True)
    
    def __repr__(self) -> str:
        return f"Client(environment='{self.environment}', base_url='{self.base_url}')"
