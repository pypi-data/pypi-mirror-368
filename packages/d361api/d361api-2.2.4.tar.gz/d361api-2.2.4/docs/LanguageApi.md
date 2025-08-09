# d361api.LanguageApi

All URIs are relative to *https://apihub.document360.io*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_language_project_version_id_get**](LanguageApi.md#v2_language_project_version_id_get) | **GET** /v2/Language/{projectVersionId} | Gets all version languages in the project


# **v2_language_project_version_id_get**
> GetLanguageFromProjectVersion v2_language_project_version_id_get(project_version_id)

Gets all version languages in the project

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_language_from_project_version import GetLanguageFromProjectVersion
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
    api_instance = d361api.LanguageApi(api_client)
    project_version_id = 'project_version_id_example' # str | The ID of the project version

    try:
        # Gets all version languages in the project
        api_response = await api_instance.v2_language_project_version_id_get(project_version_id)
        print("The response of LanguageApi->v2_language_project_version_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LanguageApi->v2_language_project_version_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_version_id** | **str**| The ID of the project version | 

### Return type

[**GetLanguageFromProjectVersion**](GetLanguageFromProjectVersion.md)

### Authorization

[api_token](../README.md#api_token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

