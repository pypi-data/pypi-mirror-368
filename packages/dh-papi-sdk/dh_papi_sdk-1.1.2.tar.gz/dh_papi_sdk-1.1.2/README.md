## 📋 API Modules

### VRM Bulk Operations
Complete Salesforce bulk API integration with 100% endpoint coverage.

```python
# Get bulk client
bulk = client.vrm_bulk

# Core operations
jobs = bulk.get_all_jobs()                    # List all jobs
job = bulk.create_job("Account", "insert")    # Create INSERT job
job = bulk.create_job("Account", "upsert", external_id_field="Id")  # Create UPSERT job
info = bulk.get_job_info(job_id)             # Get job status
bulk.upload_job_data(job_id, csv_data)       # Upload data
bulk.close_job(job_id)                       # Close for processing

# Results retrieval
successful = bulk.get_successful_results(job_id)   # Get successful records
failed = bulk.get_failed_results(job_id)           # Get failed records  
unprocessed = bulk.get_unprocessed_records(job_id) # Get unprocessed records

# Management
bulk.delete_job(job_id)                      # Delete job
```

**⚠️ Important Notes:**
- **UPSERT operations** currently require an SDK update to support the `external_id_field` parameter
- **INSERT operations** work with the current SDK version
- For UPSERT, you must specify an External ID field (e.g., "Id", "External_ID__c")

**📚 [Complete VRM Bulk API Documentation →](sdk/py/docs/vrm-bulk.md)**

*Includes all 9 methods, complete workflow examples, and production-ready code samples.*

## 🔍 Troubleshooting

### Common Issues

#### 1. Authentication Issues
```python
# Test connection
if client.test_connection():
    print("✅ Authentication working")
else:
    print("❌ Check credentials")
```

#### 2. UPSERT Operation Failures
```
Error: InvalidJob : External ID was blank for [Object]. An External ID must be specified for upsert.
```

**Solution:** Your current SDK version doesn't support the `external_id_field` parameter required for upsert operations.

**Workaround:** Use INSERT operations instead:
```python
# Instead of upsert, use insert for new records
job = bulk.create_job("Bank_Information__c", "insert")
```

**Permanent Fix:** Update the SDK's `create_job` method to support:
```python
def create_job(self, object_name: str, operation: str, external_id_field: str = None):
    # Implementation needed in vrm_bulk_client.py
```

#### 3. Debug Mode
```python
# Enable detailed logging in your application
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 4. APIGee Proxy Issues
If you see 403/500 errors:
- Check APIGee permissions and OAuth scopes
- Verify Salesforce backend connectivity
- Contact Platform API team with request IDs from error logs

## 🚧 Known Limitations

### Current SDK Version (v1.1.2)
- ✅ **INSERT operations**: Fully supported
- ❌ **UPSERT operations**: Requires SDK update to support `external_id_field` parameter  
- ✅ **UPDATE/DELETE operations**: Supported (standard operations)
- ✅ **All result retrieval methods**: Fully supported

### Upcoming Features
- Enhanced upsert operation support with external ID fields
- Additional validation and error handling improvements

## 🔄 Version History

- **v1.1.2** - Current release with Bulk Upsert & INSERT operations support
- 