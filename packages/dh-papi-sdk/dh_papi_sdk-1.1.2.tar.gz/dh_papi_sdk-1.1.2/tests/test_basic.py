# /sdk/py/papi-sdk/test_basic.py
"""
Basic tests for PAPI SDK - Just the essentials
"""

import pytest
from unittest.mock import Mock, patch


def test_imports_work():
    """Test that basic imports work"""
    from papi_sdk import Client, AuthClient, BulkAPI
    assert Client is not None
    assert AuthClient is not None
    assert BulkAPI is not None


@patch('papi_sdk.client.AuthClient')
def test_client_creation(mock_auth):
    """Test client can be created"""
    mock_auth_instance = Mock()
    mock_auth_instance.get_token.return_value = "test-token"
    mock_auth.return_value = mock_auth_instance
    
    from papi_sdk import Client
    
    client = Client(
        client_id="test-id",
        client_secret="test-secret",
        environment="stg"
    )
    
    assert client.environment == "stg"
    assert "stg" in client.base_url


@patch('requests.post')
def test_auth_client(mock_post):
    """Test auth client works"""
    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "test-token",
        "expires_in": 3600
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    from papi_sdk.auth import AuthClient
    
    client = AuthClient("https://test.com", "id", "secret")
    token = client.get_token()
    
    assert token == "test-token"
    mock_post.assert_called_once()


@patch('http.client.HTTPSConnection')
def test_urllib3_free_auth(mock_conn):
    """Test urllib3-free authentication works"""
    # Mock response
    mock_response = Mock()
    mock_response.status = 200
    mock_response.read.return_value = b'{"access_token": "urllib3-free-token", "expires_in": 3600}'
    
    mock_conn_instance = Mock()
    mock_conn_instance.getresponse.return_value = mock_response
    mock_conn.return_value = mock_conn_instance
    
    from papi_sdk.urllib3_free_auth import Urllib3FreeAuthClient
    
    client = Urllib3FreeAuthClient("https://test.com", "id", "secret")
    client._refresh_token()
    
    assert client._token == "urllib3-free-token"
    mock_conn.assert_called_once()


def test_vrm_bulk_client():
    """Test VRM bulk client works"""
    from papi_sdk.vrm_bulk_client import BulkAPI
    
    mock_api_client = Mock()
    
    with patch('papi_sdk.vrm_bulk_client.VrmBulkApi') as mock_api:
        mock_api_instance = Mock()
        mock_job = Mock()
        mock_job.id = "job-123"
        mock_job.state = "Open"
        mock_api_instance.vrm_v1_jobs_ingest_post.return_value = mock_job
        mock_api.return_value = mock_api_instance
        
        client = BulkAPI(mock_api_client)
        result = client.create_job("Account", "insert")
        
        assert result.id == "job-123"
        assert result.state == "Open"


@patch('papi_sdk.client.AuthClient')  
@patch('papi_sdk.client.BulkAPI')
def test_full_workflow(mock_vrm, mock_auth):
    """Test complete workflow works"""
    # Mock auth
    mock_auth_instance = Mock()
    mock_auth_instance.get_token.return_value = "workflow-token"
    mock_auth.return_value = mock_auth_instance
    
    # Mock VRM
    mock_vrm_instance = Mock()
    mock_job = Mock()
    mock_job.id = "workflow-job"
    mock_vrm_instance.create_job.return_value = mock_job
    mock_vrm_instance.upload_job_data.return_value = None
    mock_vrm_instance.close_job.return_value = Mock(state="UploadComplete")
    mock_vrm.return_value = mock_vrm_instance
    
    from papi_sdk import Client
    
    # Create client
    client = Client(
        client_id="workflow-id",
        client_secret="workflow-secret",
        environment="stg"
    )
    
    # Create job
    job = client.vrm_bulk.create_job("Contact", "insert")
    assert job.id == "workflow-job"
    
    # Upload data
    client.vrm_bulk.upload_job_data(job.id, "Name,Email\nTest,test@test.com")
    
    # Close job
    result = client.vrm_bulk.close_job(job.id)
    assert result.state == "UploadComplete"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
    