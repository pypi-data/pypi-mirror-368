# d361api.ProjectApi

All URIs are relative to *https://apihub.document360.io*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_project_export_export_id_get**](ProjectApi.md#v2_project_export_export_id_get) | **GET** /v2/Project/Export/{exportId} | Get the status of export
[**v2_project_export_post**](ProjectApi.md#v2_project_export_post) | **POST** /v2/Project/Export | Start a new export
[**v2_project_import_import_id_get**](ProjectApi.md#v2_project_import_import_id_get) | **GET** /v2/Project/Import/{importId} | Get the status of import
[**v2_project_import_post**](ProjectApi.md#v2_project_import_post) | **POST** /v2/Project/Import | Import documentation
[**v2_project_schemes_get**](ProjectApi.md#v2_project_schemes_get) | **GET** /v2/Project/Schemes | Get all the schemes for the project
[**v2_project_workflow_statuses_get**](ProjectApi.md#v2_project_workflow_statuses_get) | **GET** /v2/Project/workflow-statuses | Gets all workflow statuses for a project


# **v2_project_export_export_id_get**
> ExportDocumentationStatusResponse v2_project_export_export_id_get(export_id)

Get the status of export

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.export_documentation_status_response import ExportDocumentationStatusResponse
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
    api_instance = d361api.ProjectApi(api_client)
    export_id = 'export_id_example' # str | The ID of the export request

    try:
        # Get the status of export
        api_response = await api_instance.v2_project_export_export_id_get(export_id)
        print("The response of ProjectApi->v2_project_export_export_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectApi->v2_project_export_export_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **export_id** | **str**| The ID of the export request | 

### Return type

[**ExportDocumentationStatusResponse**](ExportDocumentationStatusResponse.md)

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

# **v2_project_export_post**
> ExportDocumentationResponse v2_project_export_post(export_documentation_request=export_documentation_request)

Start a new export

Sample requests:                    POST /Export - Export all the versions in the documentation      {         \"entity\": \"Project\", // Project / version         \"versionId\": [], // should be empty array          \"SelectedLanguages\":[],         \"SelectedCategories\":[],         \"FilterByArticleModifiedAt\": {  // filter articles by modified at date range             \"after\": \"2021-05-17T03:42:52.109Z\",              \"before\": \"2021-05-17T03:42:52.109Z\"         },         \"excludeMediaFiles\": true // exculde media files on export      }                    POST /Export - Export specific versions in the documentation      {         \"entity\": \"Version\", // Project / version         \"versionId\": [\"695782c0-a0a3-4664-9bfd-0197d26379ee\"],         \"SelectedLanguages\":[],         \"SelectedCategories\":[],         \"FilterByArticleModifiedAt\": {  // filter articles by modified at date range             \"after\": \"2021-05-17T03:42:52.109Z\",              \"before\": \"2021-05-17T03:42:52.109Z\"         },         \"excludeMediaFiles\": true // exculde media files on export      }

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.export_documentation_request import ExportDocumentationRequest
from d361api.models.export_documentation_response import ExportDocumentationResponse
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
    api_instance = d361api.ProjectApi(api_client)
    export_documentation_request = {"entity":"Project","version_id":[],"selected_languages":null,"selected_categories":null,"exclude_media_files":true,"filter_by_article_modified_at":null,"export_type":0} # ExportDocumentationRequest | Filter to export Full/Part of the documenation (optional)

    try:
        # Start a new export
        api_response = await api_instance.v2_project_export_post(export_documentation_request=export_documentation_request)
        print("The response of ProjectApi->v2_project_export_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectApi->v2_project_export_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **export_documentation_request** | [**ExportDocumentationRequest**](ExportDocumentationRequest.md)| Filter to export Full/Part of the documenation | [optional] 

### Return type

[**ExportDocumentationResponse**](ExportDocumentationResponse.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Status of the export |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_project_import_import_id_get**
> ImportDocumentationStatusResponse v2_project_import_import_id_get(import_id)

Get the status of import

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.import_documentation_status_response import ImportDocumentationStatusResponse
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
    api_instance = d361api.ProjectApi(api_client)
    import_id = 'import_id_example' # str | The ID of import request

    try:
        # Get the status of import
        api_response = await api_instance.v2_project_import_import_id_get(import_id)
        print("The response of ProjectApi->v2_project_import_import_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectApi->v2_project_import_import_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **import_id** | **str**| The ID of import request | 

### Return type

[**ImportDocumentationStatusResponse**](ImportDocumentationStatusResponse.md)

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

# **v2_project_import_post**
> ImportDocumentationResponse v2_project_import_post(import_documentation_request=import_documentation_request)

Import documentation

Sample requests:                    POST /Import - Import documention from external zip file url      {         \"source_documentation_url\": \"https://yourdomain/documentation.zip\", // Document360 standard file only accepted         \"publish_article\": true, // import article and publish                    \"import_by\": \"5a619a315481302d50b736d8\" // Document360 user id      }

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.import_documentation_request import ImportDocumentationRequest
from d361api.models.import_documentation_response import ImportDocumentationResponse
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
    api_instance = d361api.ProjectApi(api_client)
    import_documentation_request = {"source_documentation_url":"https://yourdomain/documentation.zip","publish_article":true,"import_by":"5a619a315481302d50b736d8"} # ImportDocumentationRequest |  (optional)

    try:
        # Import documentation
        api_response = await api_instance.v2_project_import_post(import_documentation_request=import_documentation_request)
        print("The response of ProjectApi->v2_project_import_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectApi->v2_project_import_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **import_documentation_request** | [**ImportDocumentationRequest**](ImportDocumentationRequest.md)|  | [optional] 

### Return type

[**ImportDocumentationResponse**](ImportDocumentationResponse.md)

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

# **v2_project_schemes_get**
> SSOSchemeReponse v2_project_schemes_get()

Get all the schemes for the project

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.sso_scheme_reponse import SSOSchemeReponse
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
    api_instance = d361api.ProjectApi(api_client)

    try:
        # Get all the schemes for the project
        api_response = await api_instance.v2_project_schemes_get()
        print("The response of ProjectApi->v2_project_schemes_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectApi->v2_project_schemes_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**SSOSchemeReponse**](SSOSchemeReponse.md)

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

# **v2_project_workflow_statuses_get**
> GetWorkflowStatusResponse v2_project_workflow_statuses_get()

Gets all workflow statuses for a project

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_workflow_status_response import GetWorkflowStatusResponse
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
    api_instance = d361api.ProjectApi(api_client)

    try:
        # Gets all workflow statuses for a project
        api_response = await api_instance.v2_project_workflow_statuses_get()
        print("The response of ProjectApi->v2_project_workflow_statuses_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectApi->v2_project_workflow_statuses_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetWorkflowStatusResponse**](GetWorkflowStatusResponse.md)

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

