# /sdk/py/papi-sdk/papi_sdk/vrm_bulk_client.py
from .generated.generated.api.vrm_bulk_api import VrmBulkApi
from .generated.generated.api_client import ApiClient
from .generated.generated.models import (
    VrmV1JobsIngestGet200Response,
    VrmV1JobsIngestJobIdGet200Response,
    VrmV1JobsIngestJobIdPatch200Response,
    VrmV1JobsIngestJobIdPatchRequest,
    VrmV1JobsIngestPost200Response,
    VrmV1JobsIngestPostRequest,
)


class BulkAPI:
    """
    A client for interacting with the VRM Bulk API, providing a simplified interface
    over the auto-generated API client.
    
    This client provides complete coverage of all 9 VRM Bulk API endpoints:
    - Job management (create, get, delete, close)
    - Data upload 
    - Results retrieval (successful, failed, unprocessed)
    """

    def __init__(self, api_client: ApiClient):
        self._api = VrmBulkApi(api_client)

    # ========================================
    # JOB MANAGEMENT METHODS
    # ========================================

    def create_job(self, object_name: str, operation: str, external_id_field: str = None) -> VrmV1JobsIngestPost200Response:
        """
        Creates a new bulk ingest job.
        
        Args:
            object_name: The Salesforce object to operate on (e.g., 'Account', 'Contact')
            operation: The operation to perform (e.g., 'insert', 'update', 'upsert', 'delete')
            external_id_field: Required for 'upsert' operations. The field to use as external ID (e.g., 'Id', 'External_ID__c')
            
        Returns:
            Job creation response containing job ID and details
            
        Raises:
            ApiException: If the request fails
            ValueError: If upsert operation is requested without external_id_field
        """
        # Validate upsert requirements
        if operation.lower() == 'upsert' and not external_id_field:
            raise ValueError("external_id_field is required for upsert operations")
        
        # Create request with or without external ID field
        if operation.lower() == 'upsert' and external_id_field:
            request = VrmV1JobsIngestPostRequest(
                object=object_name, 
                operation=operation,
                external_id_field_name=external_id_field  # This field name might vary in your generated models
            )
        else:
            request = VrmV1JobsIngestPostRequest(object=object_name, operation=operation)
        
        return self._api.vrm_v1_jobs_ingest_post(vrm_v1_jobs_ingest_post_request=request)

    def get_all_jobs(self) -> VrmV1JobsIngestGet200Response:
        """
        Retrieves information about all bulk jobs.
        
        Returns:
            Response containing list of all jobs and their details
            
        Raises:
            ApiException: If the request fails
        """
        return self._api.vrm_v1_jobs_ingest_get()

    def get_job_info(self, job_id: str) -> VrmV1JobsIngestJobIdGet200Response:
        """
        Retrieves detailed information about a specific job.
        
        Args:
            job_id: The ID of the job to query
            
        Returns:
            Job details including state, progress, and statistics
            
        Raises:
            ApiException: If the request fails or job not found
        """
        return self._api.vrm_v1_jobs_ingest_job_id_get(job_id=job_id)

    def delete_job(self, job_id: str) -> None:
        """
        Deletes a job. Job must be in UploadComplete, JobComplete, Aborted, or Failed state.
        
        Args:
            job_id: The ID of the job to delete
            
        Raises:
            ApiException: If the request fails or job cannot be deleted
        """
        return self._api.vrm_v1_jobs_ingest_job_id_delete(job_id=job_id)

    # ========================================
    # DATA UPLOAD METHODS
    # ========================================

    def upload_job_data(self, job_id: str, csv_data: str) -> None:
        """
        Uploads CSV data to an existing job.
        
        Args:
            job_id: The ID of the job to upload data to
            csv_data: CSV-formatted data as a string
            
        Raises:
            ApiException: If the request fails or job is not in correct state
        """
        return self._api.vrm_v1_jobs_ingest_job_id_batches_put(job_id=job_id, body=csv_data)

    def close_job(self, job_id: str) -> VrmV1JobsIngestJobIdPatch200Response:
        """
        Closes a job, making it available for processing.
        This is required for every bulk job - processing won't start without this call.
        
        Args:
            job_id: The ID of the job to close
            
        Returns:
            Updated job information
            
        Raises:
            ApiException: If the request fails
        """
        request = VrmV1JobsIngestJobIdPatchRequest(state="UploadComplete")
        return self._api.vrm_v1_jobs_ingest_job_id_patch(job_id=job_id, vrm_v1_jobs_ingest_job_id_patch_request=request)

    # ========================================
    # RESULTS RETRIEVAL METHODS
    # ========================================

    def get_successful_results(self, job_id: str) -> str:
        """
        Retrieves CSV data of successfully processed records for a completed job.
        
        Args:
            job_id: The ID of the completed job
            
        Returns:
            CSV string containing successful records with their assigned IDs
            
        Raises:
            ApiException: If the request fails or job is not complete
        """
        return self._api.vrm_v1_jobs_ingest_job_id_successful_results_get(job_id=job_id)

    def get_failed_results(self, job_id: str) -> str:
        """
        Retrieves CSV data of failed records for a completed job.
        
        Args:
            job_id: The ID of the completed job
            
        Returns:
            CSV string containing failed records with error messages
            
        Raises:
            ApiException: If the request fails or job is not complete
        """
        return self._api.vrm_v1_jobs_ingest_job_id_failed_results_get(job_id=job_id)

    def get_unprocessed_records(self, job_id: str) -> str:
        """
        Retrieves CSV data of unprocessed records for a completed job.
        These are records that were not processed due to various reasons.
        
        Args:
            job_id: The ID of the completed job
            
        Returns:
            CSV string containing unprocessed records
            
        Raises:
            ApiException: If the request fails or job is not complete
        """
        return self._api.vrm_v1_jobs_ingest_job_id_unprocessed_records_get(job_id=job_id)

    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def list_available_methods(self) -> list[str]:
        """
        Debug helper: List all available methods on the VRM Bulk API
        
        Returns:
            List of method names
        """
        return [method for method in dir(self._api) 
                if not method.startswith('_')]

    def get_job_results_summary(self, job_id: str) -> dict:
        """
        Convenience method to get a summary of all job results.
        
        Args:
            job_id: The ID of the completed job
            
        Returns:
            Dictionary containing job info and all results data
            
        Raises:
            ApiException: If any request fails
        """
        job_info = self.get_job_info(job_id)
        
        results = {
            'job_info': job_info,
            'successful_results': None,
            'failed_results': None,
            'unprocessed_records': None
        }
        
        # Only try to get results if job is complete
        job_state = getattr(job_info, 'state', None)
        if job_state == 'JobComplete':
            try:
                results['successful_results'] = self.get_successful_results(job_id)
            except Exception:
                pass  # May not have successful results
                
            try:
                results['failed_results'] = self.get_failed_results(job_id)
            except Exception:
                pass  # May not have failed results
                
            try:
                results['unprocessed_records'] = self.get_unprocessed_records(job_id)
            except Exception:
                pass  # May not have unprocessed records
        
        return results