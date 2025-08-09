# d361api.DriveApi

All URIs are relative to *https://apihub.document360.io*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_drive_folders_delete_file_status_task_id_get**](DriveApi.md#v2_drive_folders_delete_file_status_task_id_get) | **GET** /v2/Drive/Folders/DeleteFile/Status/{taskId} | Get status of the delete file operation
[**v2_drive_folders_files_post**](DriveApi.md#v2_drive_folders_files_post) | **POST** /v2/Drive/Folders/Files | Add file in to drive
[**v2_drive_folders_folder_id_delete**](DriveApi.md#v2_drive_folders_folder_id_delete) | **DELETE** /v2/Drive/Folders/{folderId} | Delete a folder
[**v2_drive_folders_folder_id_file_id_copy_post**](DriveApi.md#v2_drive_folders_folder_id_file_id_copy_post) | **POST** /v2/Drive/Folders/{folderId}/{fileId}/Copy | Copy file from one folder to another
[**v2_drive_folders_folder_id_file_id_delete**](DriveApi.md#v2_drive_folders_folder_id_file_id_delete) | **DELETE** /v2/Drive/Folders/{folderId}/{fileId} | Delete file using file ID
[**v2_drive_folders_folder_id_file_id_get**](DriveApi.md#v2_drive_folders_folder_id_file_id_get) | **GET** /v2/Drive/Folders/{folderId}/{fileId} | Gets file information
[**v2_drive_folders_folder_id_file_id_put**](DriveApi.md#v2_drive_folders_folder_id_file_id_put) | **PUT** /v2/Drive/Folders/{folderId}/{fileId} | Move a file with file ID
[**v2_drive_folders_folder_id_file_id_tags_bulkdelete_post**](DriveApi.md#v2_drive_folders_folder_id_file_id_tags_bulkdelete_post) | **POST** /v2/Drive/Folders/{folderId}/{fileId}/Tags/Bulkdelete | Delete tags from files
[**v2_drive_folders_folder_id_file_id_tags_post**](DriveApi.md#v2_drive_folders_folder_id_file_id_tags_post) | **POST** /v2/Drive/Folders/{folderId}/{fileId}/Tags | Add tags in a file using file ID
[**v2_drive_folders_folder_id_get**](DriveApi.md#v2_drive_folders_folder_id_get) | **GET** /v2/Drive/Folders/{folderId} | Gets folder information by folder ID
[**v2_drive_folders_get**](DriveApi.md#v2_drive_folders_get) | **GET** /v2/Drive/Folders | Gets folders information
[**v2_drive_folders_post**](DriveApi.md#v2_drive_folders_post) | **POST** /v2/Drive/Folders | Add new folder in drive
[**v2_drive_folders_put**](DriveApi.md#v2_drive_folders_put) | **PUT** /v2/Drive/Folders | Update a folder with ID
[**v2_drive_media_files_project_version_id_article_id_lang_code_get**](DriveApi.md#v2_drive_media_files_project_version_id_article_id_lang_code_get) | **GET** /v2/Drive/MediaFiles/{projectVersionId}/{articleId}/{langCode} | Get all media files inserted in the article
[**v2_drive_search_get**](DriveApi.md#v2_drive_search_get) | **GET** /v2/Drive/Search | Drive search - files and folders


# **v2_drive_folders_delete_file_status_task_id_get**
> GetCustomerTaskStatusResponse v2_drive_folders_delete_file_status_task_id_get(task_id)

Get status of the delete file operation

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_customer_task_status_response import GetCustomerTaskStatusResponse
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    task_id = 'task_id_example' # str | The task ID of the file deleted

    try:
        # Get status of the delete file operation
        api_response = await api_instance.v2_drive_folders_delete_file_status_task_id_get(task_id)
        print("The response of DriveApi->v2_drive_folders_delete_file_status_task_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_folders_delete_file_status_task_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **task_id** | **str**| The task ID of the file deleted | 

### Return type

[**GetCustomerTaskStatusResponse**](GetCustomerTaskStatusResponse.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_folders_files_post**
> AddMediaFileResponseCustomer v2_drive_folders_files_post(drive_folder_id, user_id, files)

Add file in to drive

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.add_media_file_response_customer import AddMediaFileResponseCustomer
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    drive_folder_id = 'drive_folder_id_example' # str | The folder ID
    user_id = 'user_id_example' # str | The ID of the team account
    files = None # List[bytearray] | File collection -The maximum file size upload limit is 40MB

    try:
        # Add file in to drive
        api_response = await api_instance.v2_drive_folders_files_post(drive_folder_id, user_id, files)
        print("The response of DriveApi->v2_drive_folders_files_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_folders_files_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **drive_folder_id** | **str**| The folder ID | 
 **user_id** | **str**| The ID of the team account | 
 **files** | **List[bytearray]**| File collection -The maximum file size upload limit is 40MB | 

### Return type

[**AddMediaFileResponseCustomer**](AddMediaFileResponseCustomer.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_folders_folder_id_delete**
> CustomerApiBaseResponse v2_drive_folders_folder_id_delete(folder_id)

Delete a folder

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.customer_api_base_response import CustomerApiBaseResponse
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    folder_id = 'folder_id_example' # str | The ID of the folder in Drive

    try:
        # Delete a folder
        api_response = await api_instance.v2_drive_folders_folder_id_delete(folder_id)
        print("The response of DriveApi->v2_drive_folders_folder_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_folders_folder_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| The ID of the folder in Drive | 

### Return type

[**CustomerApiBaseResponse**](CustomerApiBaseResponse.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_folders_folder_id_file_id_copy_post**
> CustomerApiBaseResponse v2_drive_folders_folder_id_file_id_copy_post(folder_id, file_id)

Copy file from one folder to another

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.customer_api_base_response import CustomerApiBaseResponse
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    folder_id = 'folder_id_example' # str | Target folder ID
    file_id = 'file_id_example' # str | Selected file ID

    try:
        # Copy file from one folder to another
        api_response = await api_instance.v2_drive_folders_folder_id_file_id_copy_post(folder_id, file_id)
        print("The response of DriveApi->v2_drive_folders_folder_id_file_id_copy_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_folders_folder_id_file_id_copy_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| Target folder ID | 
 **file_id** | **str**| Selected file ID | 

### Return type

[**CustomerApiBaseResponse**](CustomerApiBaseResponse.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_folders_folder_id_file_id_delete**
> DeleteMediaFileResponseCustomer v2_drive_folders_folder_id_file_id_delete(folder_id, file_id)

Delete file using file ID

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.delete_media_file_response_customer import DeleteMediaFileResponseCustomer
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    folder_id = 'folder_id_example' # str | The ID of the folder in Drive
    file_id = 'file_id_example' # str | The ID of the file in Drive

    try:
        # Delete file using file ID
        api_response = await api_instance.v2_drive_folders_folder_id_file_id_delete(folder_id, file_id)
        print("The response of DriveApi->v2_drive_folders_folder_id_file_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_folders_folder_id_file_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| The ID of the folder in Drive | 
 **file_id** | **str**| The ID of the file in Drive | 

### Return type

[**DeleteMediaFileResponseCustomer**](DeleteMediaFileResponseCustomer.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_folders_folder_id_file_id_get**
> MediaFileAndTagsMetaDataResponseCustomer v2_drive_folders_folder_id_file_id_get(folder_id, file_id, append_sas_token=append_sas_token)

Gets file information

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.media_file_and_tags_meta_data_response_customer import MediaFileAndTagsMetaDataResponseCustomer
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    folder_id = 'folder_id_example' # str | The ID of drive folder
    file_id = 'file_id_example' # str | The ID of file
    append_sas_token = False # bool | Set this to false to exclude appending SAS token for images/files (optional) (default to False)

    try:
        # Gets file information
        api_response = await api_instance.v2_drive_folders_folder_id_file_id_get(folder_id, file_id, append_sas_token=append_sas_token)
        print("The response of DriveApi->v2_drive_folders_folder_id_file_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_folders_folder_id_file_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| The ID of drive folder | 
 **file_id** | **str**| The ID of file | 
 **append_sas_token** | **bool**| Set this to false to exclude appending SAS token for images/files | [optional] [default to False]

### Return type

[**MediaFileAndTagsMetaDataResponseCustomer**](MediaFileAndTagsMetaDataResponseCustomer.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_folders_folder_id_file_id_put**
> CustomerApiBaseResponse v2_drive_folders_folder_id_file_id_put(folder_id, file_id)

Move a file with file ID

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.customer_api_base_response import CustomerApiBaseResponse
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    folder_id = 'folder_id_example' # str | The ID of target folder
    file_id = 'file_id_example' # str | The ID of file

    try:
        # Move a file with file ID
        api_response = await api_instance.v2_drive_folders_folder_id_file_id_put(folder_id, file_id)
        print("The response of DriveApi->v2_drive_folders_folder_id_file_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_folders_folder_id_file_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| The ID of target folder | 
 **file_id** | **str**| The ID of file | 

### Return type

[**CustomerApiBaseResponse**](CustomerApiBaseResponse.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_folders_folder_id_file_id_tags_bulkdelete_post**
> MediaFileDataResponseCustomer v2_drive_folders_folder_id_file_id_tags_bulkdelete_post(folder_id, file_id, user_id, request_body)

Delete tags from files

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.media_file_data_response_customer import MediaFileDataResponseCustomer
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    folder_id = 'folder_id_example' # str | The folder ID
    file_id = 'file_id_example' # str | The file ID
    user_id = 'user_id_example' # str | Team account ID
    request_body = ['request_body_example'] # List[str] | List of tag Ids

    try:
        # Delete tags from files
        api_response = await api_instance.v2_drive_folders_folder_id_file_id_tags_bulkdelete_post(folder_id, file_id, user_id, request_body)
        print("The response of DriveApi->v2_drive_folders_folder_id_file_id_tags_bulkdelete_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_folders_folder_id_file_id_tags_bulkdelete_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| The folder ID | 
 **file_id** | **str**| The file ID | 
 **user_id** | **str**| Team account ID | 
 **request_body** | [**List[str]**](str.md)| List of tag Ids | 

### Return type

[**MediaFileDataResponseCustomer**](MediaFileDataResponseCustomer.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_folders_folder_id_file_id_tags_post**
> MediaFileDataResponseCustomer v2_drive_folders_folder_id_file_id_tags_post(folder_id, file_id, user_id, request_body)

Add tags in a file using file ID

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.media_file_data_response_customer import MediaFileDataResponseCustomer
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    folder_id = 'folder_id_example' # str | The folder ID
    file_id = 'file_id_example' # str | The file ID
    user_id = 'user_id_example' # str | Team account ID
    request_body = ['request_body_example'] # List[str] | List of tag names

    try:
        # Add tags in a file using file ID
        api_response = await api_instance.v2_drive_folders_folder_id_file_id_tags_post(folder_id, file_id, user_id, request_body)
        print("The response of DriveApi->v2_drive_folders_folder_id_file_id_tags_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_folders_folder_id_file_id_tags_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| The folder ID | 
 **file_id** | **str**| The file ID | 
 **user_id** | **str**| Team account ID | 
 **request_body** | [**List[str]**](str.md)| List of tag names | 

### Return type

[**MediaFileDataResponseCustomer**](MediaFileDataResponseCustomer.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_folders_folder_id_get**
> GetMediaFolderWithIdCustomer v2_drive_folders_folder_id_get(folder_id, append_sas_token=append_sas_token, page_no=page_no, take=take)

Gets folder information by folder ID

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_media_folder_with_id_customer import GetMediaFolderWithIdCustomer
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    folder_id = 'folder_id_example' # str | The ID of the folder in Drive
    append_sas_token = False # bool | Set this to false to exclude appending SAS token for images/files (optional) (default to False)
    page_no = 0 # int | Specify the page to retrieve. Page numbers are zero-based. Therefore, to retrieve the 10th page, you need to set page=9 (optional) (default to 0)
    take = 20 # int | The number of results per page (optional) (default to 20)

    try:
        # Gets folder information by folder ID
        api_response = await api_instance.v2_drive_folders_folder_id_get(folder_id, append_sas_token=append_sas_token, page_no=page_no, take=take)
        print("The response of DriveApi->v2_drive_folders_folder_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_folders_folder_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| The ID of the folder in Drive | 
 **append_sas_token** | **bool**| Set this to false to exclude appending SAS token for images/files | [optional] [default to False]
 **page_no** | **int**| Specify the page to retrieve. Page numbers are zero-based. Therefore, to retrieve the 10th page, you need to set page&#x3D;9 | [optional] [default to 0]
 **take** | **int**| The number of results per page | [optional] [default to 20]

### Return type

[**GetMediaFolderWithIdCustomer**](GetMediaFolderWithIdCustomer.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_folders_get**
> GetMediaFolderResponseCustomer v2_drive_folders_get()

Gets folders information

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_media_folder_response_customer import GetMediaFolderResponseCustomer
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)

    try:
        # Gets folders information
        api_response = await api_instance.v2_drive_folders_get()
        print("The response of DriveApi->v2_drive_folders_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_folders_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetMediaFolderResponseCustomer**](GetMediaFolderResponseCustomer.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_folders_post**
> MediaFolderMetaDataResponseCustomer v2_drive_folders_post(add_media_folder_request_customer=add_media_folder_request_customer)

Add new folder in drive

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.add_media_folder_request_customer import AddMediaFolderRequestCustomer
from d361api.models.media_folder_meta_data_response_customer import MediaFolderMetaDataResponseCustomer
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    add_media_folder_request_customer = {"title":"Title","parent_folder_id":"d8b65d24-ce62-407a-8463-846efc8eee93","user_id":"ffb65d24-ce62-407a-84d-8dfdfefc8eee93","order":1} # AddMediaFolderRequestCustomer |  (optional)

    try:
        # Add new folder in drive
        api_response = await api_instance.v2_drive_folders_post(add_media_folder_request_customer=add_media_folder_request_customer)
        print("The response of DriveApi->v2_drive_folders_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_folders_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **add_media_folder_request_customer** | [**AddMediaFolderRequestCustomer**](AddMediaFolderRequestCustomer.md)|  | [optional] 

### Return type

[**MediaFolderMetaDataResponseCustomer**](MediaFolderMetaDataResponseCustomer.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_folders_put**
> MediaFolderMetaDataResponseCustomer v2_drive_folders_put(folder_id, update_media_folder_request_customer)

Update a folder with ID

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.media_folder_meta_data_response_customer import MediaFolderMetaDataResponseCustomer
from d361api.models.update_media_folder_request_customer import UpdateMediaFolderRequestCustomer
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    folder_id = 'folder_id_example' # str | The ID of drive folder
    update_media_folder_request_customer = {"name":"Updated folder name","order":2,"folder_color":"#8852F5","is_starred":true} # UpdateMediaFolderRequestCustomer | 

    try:
        # Update a folder with ID
        api_response = await api_instance.v2_drive_folders_put(folder_id, update_media_folder_request_customer)
        print("The response of DriveApi->v2_drive_folders_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_folders_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| The ID of drive folder | 
 **update_media_folder_request_customer** | [**UpdateMediaFolderRequestCustomer**](UpdateMediaFolderRequestCustomer.md)|  | 

### Return type

[**MediaFolderMetaDataResponseCustomer**](MediaFolderMetaDataResponseCustomer.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_media_files_project_version_id_article_id_lang_code_get**
> GetDriveFilesInArticleDataCustomer v2_drive_media_files_project_version_id_article_id_lang_code_get(project_version_id, article_id, lang_code, append_sas_token=append_sas_token)

Get all media files inserted in the article

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_drive_files_in_article_data_customer import GetDriveFilesInArticleDataCustomer
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    project_version_id = 'project_version_id_example' # str | The ID of the project version
    article_id = 'article_id_example' # str | The ID of the article
    lang_code = 'lang_code_example' # str | Language code of the article
    append_sas_token = False # bool | Set this to false to exclude appending SAS token for images/files (optional) (default to False)

    try:
        # Get all media files inserted in the article
        api_response = await api_instance.v2_drive_media_files_project_version_id_article_id_lang_code_get(project_version_id, article_id, lang_code, append_sas_token=append_sas_token)
        print("The response of DriveApi->v2_drive_media_files_project_version_id_article_id_lang_code_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_media_files_project_version_id_article_id_lang_code_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_version_id** | **str**| The ID of the project version | 
 **article_id** | **str**| The ID of the article | 
 **lang_code** | **str**| Language code of the article | 
 **append_sas_token** | **bool**| Set this to false to exclude appending SAS token for images/files | [optional] [default to False]

### Return type

[**GetDriveFilesInArticleDataCustomer**](GetDriveFilesInArticleDataCustomer.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_drive_search_get**
> AllFilesWithCountResponseCustomer v2_drive_search_get(search_keyword=search_keyword, page_no=page_no, take=take, allow_images_only=allow_images_only, user_ids=user_ids, filter_from_date=filter_from_date, filter_to_date=filter_to_date, filter_tags=filter_tags)

Drive search - files and folders

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.all_files_with_count_response_customer import AllFilesWithCountResponseCustomer
from d361api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://apihub.document360.io
# See configuration.py for a list of all supported configuration parameters.
configuration = d361api.Configuration(
    host = "https://apihub.document360.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_token
configuration.api_key['api_token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_token'] = 'Bearer'

# Enter a context with an instance of the API client
async with d361api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = d361api.DriveApi(api_client)
    search_keyword = 'search_keyword_example' # str | Keyword to search file items from drive (optional)
    page_no = 0 # int | Specify the page to retrieve. Page numbers are zero-based. Therefore, to retrieve the 10th page, you need to set page=9 (optional) (default to 0)
    take = 20 # int | The number of results per page (optional) (default to 20)
    allow_images_only = False # bool | Allow images only in response (optional) (default to False)
    user_ids = ['user_ids_example'] # List[str] | Find by userId (optional)
    filter_from_date = '2013-10-20T19:20:30+01:00' # datetime | Filter using from-date (optional)
    filter_to_date = '2013-10-20T19:20:30+01:00' # datetime | Filter using to-date (optional)
    filter_tags = ['filter_tags_example'] # List[str] | Filter using tagIds (optional)

    try:
        # Drive search - files and folders
        api_response = await api_instance.v2_drive_search_get(search_keyword=search_keyword, page_no=page_no, take=take, allow_images_only=allow_images_only, user_ids=user_ids, filter_from_date=filter_from_date, filter_to_date=filter_to_date, filter_tags=filter_tags)
        print("The response of DriveApi->v2_drive_search_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DriveApi->v2_drive_search_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_keyword** | **str**| Keyword to search file items from drive | [optional] 
 **page_no** | **int**| Specify the page to retrieve. Page numbers are zero-based. Therefore, to retrieve the 10th page, you need to set page&#x3D;9 | [optional] [default to 0]
 **take** | **int**| The number of results per page | [optional] [default to 20]
 **allow_images_only** | **bool**| Allow images only in response | [optional] [default to False]
 **user_ids** | [**List[str]**](str.md)| Find by userId | [optional] 
 **filter_from_date** | **datetime**| Filter using from-date | [optional] 
 **filter_to_date** | **datetime**| Filter using to-date | [optional] 
 **filter_tags** | [**List[str]**](str.md)| Filter using tagIds | [optional] 

### Return type

[**AllFilesWithCountResponseCustomer**](AllFilesWithCountResponseCustomer.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

