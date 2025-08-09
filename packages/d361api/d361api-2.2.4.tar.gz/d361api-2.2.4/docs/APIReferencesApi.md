# d361api.APIReferencesApi

All URIs are relative to *https://apihub.document360.io*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_api_references_api_reference_id_logs_get**](APIReferencesApi.md#v2_api_references_api_reference_id_logs_get) | **GET** /v2/APIReferences/{apiReferenceId}/Logs | Get all API reference logs
[**v2_api_references_api_reference_id_logs_log_id_get**](APIReferencesApi.md#v2_api_references_api_reference_id_logs_log_id_get) | **GET** /v2/APIReferences/{apiReferenceId}/Logs/{logId} | Get errors and alerts of a log
[**v2_api_references_delete**](APIReferencesApi.md#v2_api_references_delete) | **DELETE** /v2/APIReferences | Deletes an API reference
[**v2_api_references_post**](APIReferencesApi.md#v2_api_references_post) | **POST** /v2/APIReferences | Import the API reference spec file
[**v2_api_references_publish_post**](APIReferencesApi.md#v2_api_references_publish_post) | **POST** /v2/APIReferences/publish | Publishes an API reference
[**v2_api_references_put**](APIReferencesApi.md#v2_api_references_put) | **PUT** /v2/APIReferences | Resync the API reference spec file


# **v2_api_references_api_reference_id_logs_get**
> ApiReferenceLogsWrapResponseCustomer v2_api_references_api_reference_id_logs_get(api_reference_id, page=page, results_per_page=results_per_page)

Get all API reference logs

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.api_reference_logs_wrap_response_customer import ApiReferenceLogsWrapResponseCustomer
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
    api_instance = d361api.APIReferencesApi(api_client)
    api_reference_id = 'api_reference_id_example' # str | The ID of the API reference
    page = 1 # int | Page number (optional) (default to 1)
    results_per_page = 5 # int | Total logs per page (optional) (default to 5)

    try:
        # Get all API reference logs
        api_response = await api_instance.v2_api_references_api_reference_id_logs_get(api_reference_id, page=page, results_per_page=results_per_page)
        print("The response of APIReferencesApi->v2_api_references_api_reference_id_logs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIReferencesApi->v2_api_references_api_reference_id_logs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_reference_id** | **str**| The ID of the API reference | 
 **page** | **int**| Page number | [optional] [default to 1]
 **results_per_page** | **int**| Total logs per page | [optional] [default to 5]

### Return type

[**ApiReferenceLogsWrapResponseCustomer**](ApiReferenceLogsWrapResponseCustomer.md)

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

# **v2_api_references_api_reference_id_logs_log_id_get**
> GetLogsDetailsResponseCustomer v2_api_references_api_reference_id_logs_log_id_get(api_reference_id, log_id)

Get errors and alerts of a log

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_logs_details_response_customer import GetLogsDetailsResponseCustomer
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
    api_instance = d361api.APIReferencesApi(api_client)
    api_reference_id = 'api_reference_id_example' # str | The ID of the API reference
    log_id = 'log_id_example' # str | The ID of the log

    try:
        # Get errors and alerts of a log
        api_response = await api_instance.v2_api_references_api_reference_id_logs_log_id_get(api_reference_id, log_id)
        print("The response of APIReferencesApi->v2_api_references_api_reference_id_logs_log_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIReferencesApi->v2_api_references_api_reference_id_logs_log_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_reference_id** | **str**| The ID of the API reference | 
 **log_id** | **str**| The ID of the log | 

### Return type

[**GetLogsDetailsResponseCustomer**](GetLogsDetailsResponseCustomer.md)

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

# **v2_api_references_delete**
> DeleteApiReferenceResponseCustomer v2_api_references_delete(project_version_id, api_reference_id)

Deletes an API reference

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.delete_api_reference_response_customer import DeleteApiReferenceResponseCustomer
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
    api_instance = d361api.APIReferencesApi(api_client)
    project_version_id = 'project_version_id_example' # str | The ID of the project version
    api_reference_id = 'api_reference_id_example' # str | The ID ofthe API reference

    try:
        # Deletes an API reference
        api_response = await api_instance.v2_api_references_delete(project_version_id, api_reference_id)
        print("The response of APIReferencesApi->v2_api_references_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIReferencesApi->v2_api_references_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_version_id** | **str**| The ID of the project version | 
 **api_reference_id** | **str**| The ID ofthe API reference | 

### Return type

[**DeleteApiReferenceResponseCustomer**](DeleteApiReferenceResponseCustomer.md)

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

# **v2_api_references_post**
> ApiDocumentationImportResponseCustomer v2_api_references_post(project_version_id, user_id, force_import, url=url, file=file)

Import the API reference spec file

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.api_documentation_import_response_customer import ApiDocumentationImportResponseCustomer
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
    api_instance = d361api.APIReferencesApi(api_client)
    project_version_id = 'project_version_id_example' # str | The ID of the project version
    user_id = 'user_id_example' # str | The ID of the team account
    force_import = True # bool | **true** : The errors and alerts will not be shown while importing the spec file            **false** : The errors and alerts will be shown while importing the spec file (default to True)
    url = 'url_example' # str | Url of the spec file (optional)
    file = None # bytearray | File path of the spec file (optional)

    try:
        # Import the API reference spec file
        api_response = await api_instance.v2_api_references_post(project_version_id, user_id, force_import, url=url, file=file)
        print("The response of APIReferencesApi->v2_api_references_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIReferencesApi->v2_api_references_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_version_id** | **str**| The ID of the project version | 
 **user_id** | **str**| The ID of the team account | 
 **force_import** | **bool**| **true** : The errors and alerts will not be shown while importing the spec file            **false** : The errors and alerts will be shown while importing the spec file | [default to True]
 **url** | **str**| Url of the spec file | [optional] 
 **file** | **bytearray**| File path of the spec file | [optional] 

### Return type

[**ApiDocumentationImportResponseCustomer**](ApiDocumentationImportResponseCustomer.md)

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

# **v2_api_references_publish_post**
> CustomerApiBaseResponse v2_api_references_publish_post(api_reference_publish_request_customer=api_reference_publish_request_customer)

Publishes an API reference

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.api_reference_publish_request_customer import ApiReferencePublishRequestCustomer
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
    api_instance = d361api.APIReferencesApi(api_client)
    api_reference_publish_request_customer = {"api_reference_id":"5b291e6b-fa40-4ab9-941e-f8fffc23b376","project_version_id":"46f48bc7-760f-4b07-b2d2-fce4aa8ba234","user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8"} # ApiReferencePublishRequestCustomer |  (optional)

    try:
        # Publishes an API reference
        api_response = await api_instance.v2_api_references_publish_post(api_reference_publish_request_customer=api_reference_publish_request_customer)
        print("The response of APIReferencesApi->v2_api_references_publish_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIReferencesApi->v2_api_references_publish_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_reference_publish_request_customer** | [**ApiReferencePublishRequestCustomer**](ApiReferencePublishRequestCustomer.md)|  | [optional] 

### Return type

[**CustomerApiBaseResponse**](CustomerApiBaseResponse.md)

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

# **v2_api_references_put**
> ApiDocumentationResyncResponseCustomer v2_api_references_put(api_reference_id, project_version_id, user_id, force_import, url=url, file=file)

Resync the API reference spec file

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.api_documentation_resync_response_customer import ApiDocumentationResyncResponseCustomer
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
    api_instance = d361api.APIReferencesApi(api_client)
    api_reference_id = 'api_reference_id_example' # str | The ID of the API reference
    project_version_id = 'project_version_id_example' # str | The ID of the project version
    user_id = 'user_id_example' # str | The ID of the team account
    force_import = True # bool | **true** : The errors and alerts will not be shown while resyncing the spec file       **false** : The errors and alerts will be shown while resyncing the spec file (default to True)
    url = 'url_example' # str | Url of the spec file (optional)
    file = None # bytearray | File path of the spec file (optional)

    try:
        # Resync the API reference spec file
        api_response = await api_instance.v2_api_references_put(api_reference_id, project_version_id, user_id, force_import, url=url, file=file)
        print("The response of APIReferencesApi->v2_api_references_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIReferencesApi->v2_api_references_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_reference_id** | **str**| The ID of the API reference | 
 **project_version_id** | **str**| The ID of the project version | 
 **user_id** | **str**| The ID of the team account | 
 **force_import** | **bool**| **true** : The errors and alerts will not be shown while resyncing the spec file       **false** : The errors and alerts will be shown while resyncing the spec file | [default to True]
 **url** | **str**| Url of the spec file | [optional] 
 **file** | **bytearray**| File path of the spec file | [optional] 

### Return type

[**ApiDocumentationResyncResponseCustomer**](ApiDocumentationResyncResponseCustomer.md)

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

