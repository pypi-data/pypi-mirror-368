# d361api.ProjectVersionsApi

All URIs are relative to *https://apihub.document360.io*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_project_versions_ask_eddy_post**](ProjectVersionsApi.md#v2_project_versions_ask_eddy_post) | **POST** /v2/ProjectVersions/ask-eddy | Perform AI assistive search within project version
[**v2_project_versions_get**](ProjectVersionsApi.md#v2_project_versions_get) | **GET** /v2/ProjectVersions | Gets list of project versions
[**v2_project_versions_project_version_id_apireferences_get**](ProjectVersionsApi.md#v2_project_versions_project_version_id_apireferences_get) | **GET** /v2/ProjectVersions/{projectVersionId}/apireferences | Gets list of api reference within project version
[**v2_project_versions_project_version_id_articles_get**](ProjectVersionsApi.md#v2_project_versions_project_version_id_articles_get) | **GET** /v2/ProjectVersions/{projectVersionId}/articles | Gets list of articles within project version
[**v2_project_versions_project_version_id_categories_get**](ProjectVersionsApi.md#v2_project_versions_project_version_id_categories_get) | **GET** /v2/ProjectVersions/{projectVersionId}/categories | Gets list of categories within project version
[**v2_project_versions_project_version_id_lang_code_get**](ProjectVersionsApi.md#v2_project_versions_project_version_id_lang_code_get) | **GET** /v2/ProjectVersions/{projectVersionId}/{langCode} | Searches for a phrase inside project version


# **v2_project_versions_ask_eddy_post**
> AIAssistiveSearch v2_project_versions_ask_eddy_post(ai_assistive_search_request=ai_assistive_search_request)

Perform AI assistive search within project version

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.ai_assistive_search import AIAssistiveSearch
from d361api.models.ai_assistive_search_request import AIAssistiveSearchRequest
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
    api_instance = d361api.ProjectVersionsApi(api_client)
    ai_assistive_search_request = d361api.AIAssistiveSearchRequest() # AIAssistiveSearchRequest |  (optional)

    try:
        # Perform AI assistive search within project version
        api_response = await api_instance.v2_project_versions_ask_eddy_post(ai_assistive_search_request=ai_assistive_search_request)
        print("The response of ProjectVersionsApi->v2_project_versions_ask_eddy_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectVersionsApi->v2_project_versions_ask_eddy_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ai_assistive_search_request** | [**AIAssistiveSearchRequest**](AIAssistiveSearchRequest.md)|  | [optional] 

### Return type

[**AIAssistiveSearch**](AIAssistiveSearch.md)

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

# **v2_project_versions_get**
> GetProjectVersionsResponse v2_project_versions_get()

Gets list of project versions

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_project_versions_response import GetProjectVersionsResponse
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
    api_instance = d361api.ProjectVersionsApi(api_client)

    try:
        # Gets list of project versions
        api_response = await api_instance.v2_project_versions_get()
        print("The response of ProjectVersionsApi->v2_project_versions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectVersionsApi->v2_project_versions_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetProjectVersionsResponse**](GetProjectVersionsResponse.md)

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

# **v2_project_versions_project_version_id_apireferences_get**
> GetApiReferenceDataResponseCustomer v2_project_versions_project_version_id_apireferences_get(project_version_id)

Gets list of api reference within project version

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_api_reference_data_response_customer import GetApiReferenceDataResponseCustomer
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
    api_instance = d361api.ProjectVersionsApi(api_client)
    project_version_id = 'project_version_id_example' # str | 

    try:
        # Gets list of api reference within project version
        api_response = await api_instance.v2_project_versions_project_version_id_apireferences_get(project_version_id)
        print("The response of ProjectVersionsApi->v2_project_versions_project_version_id_apireferences_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectVersionsApi->v2_project_versions_project_version_id_apireferences_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_version_id** | **str**|  | 

### Return type

[**GetApiReferenceDataResponseCustomer**](GetApiReferenceDataResponseCustomer.md)

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

# **v2_project_versions_project_version_id_articles_get**
> GetArticlesResponseCustomer v2_project_versions_project_version_id_articles_get(project_version_id, lang_code=lang_code)

Gets list of articles within project version

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_articles_response_customer import GetArticlesResponseCustomer
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
    api_instance = d361api.ProjectVersionsApi(api_client)
    project_version_id = 'project_version_id_example' # str | The ID of the project version
    lang_code = 'lang_code_example' # str | Get article in the project version that corresponds to the given language code. If the language code is empty, the default language of the project version will be taken into account (optional)

    try:
        # Gets list of articles within project version
        api_response = await api_instance.v2_project_versions_project_version_id_articles_get(project_version_id, lang_code=lang_code)
        print("The response of ProjectVersionsApi->v2_project_versions_project_version_id_articles_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectVersionsApi->v2_project_versions_project_version_id_articles_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_version_id** | **str**| The ID of the project version | 
 **lang_code** | **str**| Get article in the project version that corresponds to the given language code. If the language code is empty, the default language of the project version will be taken into account | [optional] 

### Return type

[**GetArticlesResponseCustomer**](GetArticlesResponseCustomer.md)

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

# **v2_project_versions_project_version_id_categories_get**
> GetCategoriesResponse v2_project_versions_project_version_id_categories_get(project_version_id, exclude_articles=exclude_articles, lang_code=lang_code, include_category_description=include_category_description)

Gets list of categories within project version

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_categories_response import GetCategoriesResponse
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
    api_instance = d361api.ProjectVersionsApi(api_client)
    project_version_id = 'project_version_id_example' # str | The ID of the project version
    exclude_articles = True # bool | `True` - Articles will be excluded; `False` - Articles will be included (optional)
    lang_code = 'lang_code_example' # str | Get article in the project version that corresponds to the given language code. If the language code is empty, the default language of the project version will be taken into account (optional)
    include_category_description = False # bool | `True` - Include category description; `False` - Exclude category description (optional) (default to False)

    try:
        # Gets list of categories within project version
        api_response = await api_instance.v2_project_versions_project_version_id_categories_get(project_version_id, exclude_articles=exclude_articles, lang_code=lang_code, include_category_description=include_category_description)
        print("The response of ProjectVersionsApi->v2_project_versions_project_version_id_categories_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectVersionsApi->v2_project_versions_project_version_id_categories_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_version_id** | **str**| The ID of the project version | 
 **exclude_articles** | **bool**| &#x60;True&#x60; - Articles will be excluded; &#x60;False&#x60; - Articles will be included | [optional] 
 **lang_code** | **str**| Get article in the project version that corresponds to the given language code. If the language code is empty, the default language of the project version will be taken into account | [optional] 
 **include_category_description** | **bool**| &#x60;True&#x60; - Include category description; &#x60;False&#x60; - Exclude category description | [optional] [default to False]

### Return type

[**GetCategoriesResponse**](GetCategoriesResponse.md)

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

# **v2_project_versions_project_version_id_lang_code_get**
> SearchProjectVersionResponseCustomerApi v2_project_versions_project_version_id_lang_code_get(project_version_id, lang_code, search_query=search_query, page=page, hits_per_page=hits_per_page)

Searches for a phrase inside project version

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.search_project_version_response_customer_api import SearchProjectVersionResponseCustomerApi
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
    api_instance = d361api.ProjectVersionsApi(api_client)
    project_version_id = 'project_version_id_example' # str | The ID of the project version
    lang_code = 'en' # str | The language code of the article (default to 'en')
    search_query = 'search_query_example' # str | The phrase to search across all articles in the project version (optional)
    page = 0 # int | Specify the page to retrieve. Page numbers are zero-based. Therefore, to retrieve the 10th page, you need to set page=9 (optional) (default to 0)
    hits_per_page = 10 # int | Number of results per page (optional) (default to 10)

    try:
        # Searches for a phrase inside project version
        api_response = await api_instance.v2_project_versions_project_version_id_lang_code_get(project_version_id, lang_code, search_query=search_query, page=page, hits_per_page=hits_per_page)
        print("The response of ProjectVersionsApi->v2_project_versions_project_version_id_lang_code_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectVersionsApi->v2_project_versions_project_version_id_lang_code_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_version_id** | **str**| The ID of the project version | 
 **lang_code** | **str**| The language code of the article | [default to &#39;en&#39;]
 **search_query** | **str**| The phrase to search across all articles in the project version | [optional] 
 **page** | **int**| Specify the page to retrieve. Page numbers are zero-based. Therefore, to retrieve the 10th page, you need to set page&#x3D;9 | [optional] [default to 0]
 **hits_per_page** | **int**| Number of results per page | [optional] [default to 10]

### Return type

[**SearchProjectVersionResponseCustomerApi**](SearchProjectVersionResponseCustomerApi.md)

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

