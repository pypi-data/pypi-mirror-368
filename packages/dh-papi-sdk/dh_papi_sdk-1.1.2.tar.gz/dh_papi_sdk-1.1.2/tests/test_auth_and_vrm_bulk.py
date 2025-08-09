# /sdk/py/papi-sdk/tests/test_auth_and_vrm_bulk.py
"""
Fixed tests for Authentication and VRM Bulk Client
"""

import pytest
import json
from unittest.mock import Mock, patch


class TestAuthentication:
    """Test authentication functionality"""
    
    @patch('requests.post')
    def test_standard_auth_success(self, mock_post):
        """Test standard authentication works"""
        # Mock successful auth response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "auth-token-12345",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        from papi_sdk.auth import AuthClient
        
        auth_client = AuthClient(
            "https://test-api.com", 
            "test-client-id", 
            "test-client-secret"
        )
        
        # Get token should trigger auth
        token = auth_client.get_token()
        
        assert token == "auth-token-12345"
        assert auth_client._token == "auth-token-12345"
        assert auth_client._token_expires is not None
        
        # Verify correct auth request was made
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Fix: Check the actual params structure
        assert call_args[1]['params']['grant_type'] == 'client_credentials'
        assert call_args[1]['data']['client_id'] == "test-client-id"
        assert call_args[1]['data']['client_secret'] == "test-client-secret"
        assert call_args[1]['headers']['Content-Type'] == "application/x-www-form-urlencoded"
    
    @patch('requests.post')
    def test_standard_auth_error(self, mock_post):
        """Test standard authentication handles errors"""
        # Mock auth failure
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 401: Unauthorized")
        mock_post.return_value = mock_response
        
        from papi_sdk.auth import AuthClient
        
        auth_client = AuthClient("https://test-api.com", "bad-id", "bad-secret")
        
        # Fix: Match the actual error message pattern
        with pytest.raises(Exception, match="Token refresh failed"):
            auth_client.get_token()
    
    @patch('http.client.HTTPSConnection')
    def test_urllib3_free_auth_success(self, mock_https_conn):
        """Test urllib3-free authentication works"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.reason = "OK"
        mock_response.read.return_value = json.dumps({
            "access_token": "urllib3-free-token-67890",
            "expires_in": 7200,
            "token_type": "Bearer"
        }).encode('utf-8')
        
        mock_conn_instance = Mock()
        mock_conn_instance.getresponse.return_value = mock_response
        mock_https_conn.return_value = mock_conn_instance
        
        from papi_sdk.urllib3_free_auth import Urllib3FreeAuthClient
        
        auth_client = Urllib3FreeAuthClient(
            "https://test-api.com", 
            "test-client-id", 
            "test-client-secret"
        )
        
        # Test token refresh
        auth_client._refresh_token()
        
        assert auth_client._token == "urllib3-free-token-67890"
        assert auth_client._token_expires is not None
        
        # Verify http.client was used correctly
        mock_https_conn.assert_called_once()
        mock_conn_instance.request.assert_called_once()
        mock_conn_instance.close.assert_called_once()
        
        # Check request details
        request_call = mock_conn_instance.request.call_args[0]
        assert request_call[0] == "POST"  # HTTP method
        assert "/auth/v2/token" in request_call[1]  # URL path
    
    @patch('http.client.HTTPSConnection')
    def test_urllib3_free_auth_error(self, mock_https_conn):
        """Test urllib3-free authentication handles errors"""
        # Mock auth failure
        mock_response = Mock()
        mock_response.status = 401
        mock_response.reason = "Unauthorized"
        mock_response.read.return_value = b'{"error": "invalid_client"}'
        
        mock_conn_instance = Mock()
        mock_conn_instance.getresponse.return_value = mock_response
        mock_https_conn.return_value = mock_conn_instance
        
        from papi_sdk.urllib3_free_auth import Urllib3FreeAuthClient
        
        auth_client = Urllib3FreeAuthClient("https://test-api.com", "bad-id", "bad-secret")
        
        with pytest.raises(Exception, match="HTTP 401: Unauthorized"):
            auth_client._refresh_token()


class TestBulkAPI:
    """Test VRM Bulk Client functionality"""
    
    def test_create_job(self):
        """Test creating a bulk job"""
        mock_api_client = Mock()
        
        with patch('papi_sdk.vrm_bulk_client.VrmBulkApi') as mock_vrm_api:
            # Mock the API response
            mock_api_instance = Mock()
            mock_job_response = Mock()
            mock_job_response.id = "bulk-job-12345"
            mock_job_response.state = "Open"
            mock_job_response.object = "Account"
            mock_job_response.operation = "insert"
            mock_api_instance.vrm_v1_jobs_ingest_post.return_value = mock_job_response
            mock_vrm_api.return_value = mock_api_instance
            
            from papi_sdk.vrm_bulk_client import BulkAPI
            
            bulk_client = BulkAPI(mock_api_client)
            result = bulk_client.create_job("Account", "insert")
            
            assert result.id == "bulk-job-12345"
            assert result.state == "Open"
            assert result.object == "Account"
            assert result.operation == "insert"
            
            # Verify API was called correctly
            mock_api_instance.vrm_v1_jobs_ingest_post.assert_called_once()
    
    def test_upload_job_data(self):
        """Test uploading CSV data to a job"""
        mock_api_client = Mock()
        
        with patch('papi_sdk.vrm_bulk_client.VrmBulkApi') as mock_vrm_api:
            mock_api_instance = Mock()
            mock_api_instance.vrm_v1_jobs_ingest_job_id_batches_put.return_value = None
            mock_vrm_api.return_value = mock_api_instance
            
            from papi_sdk.vrm_bulk_client import BulkAPI
            
            bulk_client = BulkAPI(mock_api_client)
            csv_data = """Name,Type,Industry
"Test Corp","Customer","Technology"
"Demo Ltd","Partner","Retail"
"""
            
            result = bulk_client.upload_job_data("bulk-job-12345", csv_data)
            
            assert result is None  # Upload returns None on success
            
            # Verify API was called with correct data
            mock_api_instance.vrm_v1_jobs_ingest_job_id_batches_put.assert_called_once_with(
                job_id="bulk-job-12345",
                body=csv_data
            )
    
    def test_close_job(self):
        """Test closing a job for processing"""
        mock_api_client = Mock()
        
        with patch('papi_sdk.vrm_bulk_client.VrmBulkApi') as mock_vrm_api:
            mock_api_instance = Mock()
            mock_close_response = Mock()
            mock_close_response.state = "UploadComplete"
            mock_close_response.id = "bulk-job-12345"
            mock_api_instance.vrm_v1_jobs_ingest_job_id_patch.return_value = mock_close_response
            mock_vrm_api.return_value = mock_api_instance
            
            from papi_sdk.vrm_bulk_client import BulkAPI
            
            bulk_client = BulkAPI(mock_api_client)
            result = bulk_client.close_job("bulk-job-12345")
            
            assert result.state == "UploadComplete"
            assert result.id == "bulk-job-12345"
            
            # Verify API was called correctly
            mock_api_instance.vrm_v1_jobs_ingest_job_id_patch.assert_called_once()
    
    def test_get_job_info(self):
        """Test getting job status information"""
        mock_api_client = Mock()
        
        with patch('papi_sdk.vrm_bulk_client.VrmBulkApi') as mock_vrm_api:
            mock_api_instance = Mock()
            mock_job_info = Mock()
            mock_job_info.id = "bulk-job-12345"
            mock_job_info.state = "JobComplete"
            mock_job_info.object = "Account"
            mock_job_info.operation = "insert"
            mock_job_info.created_date = "2023-01-01T12:00:00Z"
            mock_api_instance.vrm_v1_jobs_ingest_job_id_get.return_value = mock_job_info
            mock_vrm_api.return_value = mock_api_instance
            
            from papi_sdk.vrm_bulk_client import BulkAPI
            
            bulk_client = BulkAPI(mock_api_client)
            result = bulk_client.get_job_info("bulk-job-12345")
            
            assert result.id == "bulk-job-12345"
            assert result.state == "JobComplete"
            assert result.object == "Account"
            assert result.operation == "insert"
            
            # Verify API was called correctly
            mock_api_instance.vrm_v1_jobs_ingest_job_id_get.assert_called_once_with(
                job_id="bulk-job-12345"
            )


class TestIntegratedWorkflow:
    """Test complete workflow with auth + VRM operations"""
    
    @patch('papi_sdk.client.AuthClient')
    @patch('papi_sdk.client.BulkAPI')
    def test_complete_bulk_workflow(self, mock_vrm_bulk_class, mock_auth_class):
        """Test complete workflow: auth → create job → upload → close → check status"""
        
        # Mock authentication
        mock_auth_instance = Mock()
        mock_auth_instance.get_token.return_value = "workflow-token-12345"
        mock_auth_class.return_value = mock_auth_instance
        
        # Mock VRM bulk operations
        mock_vrm_instance = Mock()
        
        # Create job response
        mock_job = Mock()
        mock_job.id = "workflow-job-12345"
        mock_job.state = "Open"
        mock_vrm_instance.create_job.return_value = mock_job
        
        # Upload response (None = success)
        mock_vrm_instance.upload_job_data.return_value = None
        
        # Close job response
        mock_close_result = Mock()
        mock_close_result.state = "UploadComplete"
        mock_vrm_instance.close_job.return_value = mock_close_result
        
        # Job status response
        mock_job_status = Mock()
        mock_job_status.id = "workflow-job-12345"
        mock_job_status.state = "JobComplete"
        mock_vrm_instance.get_job_info.return_value = mock_job_status
        
        mock_vrm_bulk_class.return_value = mock_vrm_instance
        
        from papi_sdk import Client
        
        # Initialize client
        client = Client(
            client_id="workflow-test-id",
            client_secret="workflow-test-secret",
            environment="stg"
        )
        
        # Step 1: Create bulk job
        job = client.vrm_bulk.create_job("Contact", "upsert")
        assert job.id == "workflow-job-12345"
        assert job.state == "Open"
        
        # Step 2: Upload CSV data
        csv_data = """FirstName,LastName,Email
John,Doe,john.doe@example.com
Jane,Smith,jane.smith@example.com
"""
        client.vrm_bulk.upload_job_data(job.id, csv_data)
        
        # Step 3: Close job for processing
        close_result = client.vrm_bulk.close_job(job.id)
        assert close_result.state == "UploadComplete"
        
        # Step 4: Check job status
        job_status = client.vrm_bulk.get_job_info(job.id)
        assert job_status.id == "workflow-job-12345"
        assert job_status.state == "JobComplete"
        
        # Verify all operations were called
        mock_vrm_instance.create_job.assert_called_once_with("Contact", "upsert")
        mock_vrm_instance.upload_job_data.assert_called_once_with(job.id, csv_data)
        mock_vrm_instance.close_job.assert_called_once_with(job.id)
        mock_vrm_instance.get_job_info.assert_called_once_with(job.id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])