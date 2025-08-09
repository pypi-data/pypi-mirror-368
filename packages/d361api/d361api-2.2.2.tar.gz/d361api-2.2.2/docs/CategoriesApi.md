# d361api.CategoriesApi

All URIs are relative to *https://apihub.document360.io*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_categories_bulkcreate_post**](CategoriesApi.md#v2_categories_bulkcreate_post) | **POST** /v2/Categories/bulkcreate | Adds multiple Categories
[**v2_categories_bulkdelete_category_versions_delete**](CategoriesApi.md#v2_categories_bulkdelete_category_versions_delete) | **DELETE** /v2/Categories/bulkdelete-category-versions | Delete multiple category versions
[**v2_categories_bulkpublish_lang_code_post**](CategoriesApi.md#v2_categories_bulkpublish_lang_code_post) | **POST** /v2/Categories/bulkpublish/{langCode} | Publishes multiple categories
[**v2_categories_bulkupdate_content_put**](CategoriesApi.md#v2_categories_bulkupdate_content_put) | **PUT** /v2/Categories/bulkupdateContent | Update multiple page categories
[**v2_categories_category_id_content_lang_code_get**](CategoriesApi.md#v2_categories_category_id_content_lang_code_get) | **GET** /v2/Categories/{categoryId}/content/{langCode} | Get category page with an ID
[**v2_categories_category_id_content_lang_code_put**](CategoriesApi.md#v2_categories_category_id_content_lang_code_put) | **PUT** /v2/Categories/{categoryId}/content/{langCode} | Update a category page content with the ID
[**v2_categories_category_id_delete**](CategoriesApi.md#v2_categories_category_id_delete) | **DELETE** /v2/Categories/{categoryId} | Deletes an category with an ID
[**v2_categories_category_id_fork_put**](CategoriesApi.md#v2_categories_category_id_fork_put) | **PUT** /v2/Categories/{categoryId}/fork | Fork category page with an id
[**v2_categories_category_id_get**](CategoriesApi.md#v2_categories_category_id_get) | **GET** /v2/Categories/{categoryId} | Get category with an ID
[**v2_categories_category_id_lang_code_publish_post**](CategoriesApi.md#v2_categories_category_id_lang_code_publish_post) | **POST** /v2/Categories/{categoryId}/{langCode}/publish | Publishes an category with an id
[**v2_categories_category_id_lang_code_settings_get**](CategoriesApi.md#v2_categories_category_id_lang_code_settings_get) | **GET** /v2/Categories/{categoryId}/{langCode}/settings | Get settings for the Category
[**v2_categories_category_id_lang_code_settings_put**](CategoriesApi.md#v2_categories_category_id_lang_code_settings_put) | **PUT** /v2/Categories/{categoryId}/{langCode}/settings | Update settings for the category
[**v2_categories_category_id_lang_code_update_description_put**](CategoriesApi.md#v2_categories_category_id_lang_code_update_description_put) | **PUT** /v2/Categories/{categoryId}/{langCode}/updateDescription | Update the category description
[**v2_categories_category_id_lang_code_version_version_number_delete**](CategoriesApi.md#v2_categories_category_id_lang_code_version_version_number_delete) | **DELETE** /v2/Categories/{categoryId}/{langCode}/version/{versionNumber} | Delete category Version
[**v2_categories_category_id_lang_codeversions_get**](CategoriesApi.md#v2_categories_category_id_lang_codeversions_get) | **GET** /v2/Categories/{categoryId}/{langCode}versions | Get category page versions
[**v2_categories_category_id_publish_post**](CategoriesApi.md#v2_categories_category_id_publish_post) | **POST** /v2/Categories/{categoryId}/publish | Publishes an category with an id
[**v2_categories_category_id_put**](CategoriesApi.md#v2_categories_category_id_put) | **PUT** /v2/Categories/{categoryId} | Update a category with the ID
[**v2_categories_category_id_settings_get**](CategoriesApi.md#v2_categories_category_id_settings_get) | **GET** /v2/Categories/{categoryId}/settings | Get settings for the Category
[**v2_categories_category_id_settings_put**](CategoriesApi.md#v2_categories_category_id_settings_put) | **PUT** /v2/Categories/{categoryId}/settings | Update settings for the category
[**v2_categories_category_id_update_category_type_put**](CategoriesApi.md#v2_categories_category_id_update_category_type_put) | **PUT** /v2/Categories/{categoryId}/updateCategoryType | Update the Category Type
[**v2_categories_category_id_update_description_put**](CategoriesApi.md#v2_categories_category_id_update_description_put) | **PUT** /v2/Categories/{categoryId}/updateDescription | Update the category description
[**v2_categories_category_id_version_version_number_delete**](CategoriesApi.md#v2_categories_category_id_version_version_number_delete) | **DELETE** /v2/Categories/{categoryId}/version/{versionNumber} | Delete category Version
[**v2_categories_category_id_versions_get**](CategoriesApi.md#v2_categories_category_id_versions_get) | **GET** /v2/Categories/{categoryId}/versions | Get category page versions
[**v2_categories_category_id_versions_lang_code_version_number_get**](CategoriesApi.md#v2_categories_category_id_versions_lang_code_version_number_get) | **GET** /v2/Categories/{categoryId}/versions/{langCode}/{versionNumber} | Get category page content with an ID
[**v2_categories_category_id_versions_version_number_get**](CategoriesApi.md#v2_categories_category_id_versions_version_number_get) | **GET** /v2/Categories/{categoryId}/versions/{versionNumber} | Get category page content with an ID
[**v2_categories_post**](CategoriesApi.md#v2_categories_post) | **POST** /v2/Categories | Adds a new category


# **v2_categories_bulkcreate_post**
> BulkCreateCategoryResponse v2_categories_bulkcreate_post(add_category_request=add_category_request)

Adds multiple Categories

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.add_category_request import AddCategoryRequest
from d361api.models.bulk_create_category_response import BulkCreateCategoryResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    add_category_request = [{"name":"New Category 1","project_version_id":"46f48bc7-760f-4b07-b2d2-fce4aa8ba234","order":0,"parent_category_id":null,"content":null,"category_type":0,"user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","content_type":null},{"name":"New Category 2","project_version_id":"46f48bc7-760f-4b07-b2d2-fce4aa8ba234","order":0,"parent_category_id":null,"content":null,"category_type":0,"user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","content_type":null}] # List[AddCategoryRequest] |  (optional)

    try:
        # Adds multiple Categories
        api_response = await api_instance.v2_categories_bulkcreate_post(add_category_request=add_category_request)
        print("The response of CategoriesApi->v2_categories_bulkcreate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_bulkcreate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **add_category_request** | [**List[AddCategoryRequest]**](AddCategoryRequest.md)|  | [optional] 

### Return type

[**BulkCreateCategoryResponse**](BulkCreateCategoryResponse.md)

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

# **v2_categories_bulkdelete_category_versions_delete**
> BulkDeleteCategoryVersionResponse v2_categories_bulkdelete_category_versions_delete(category_id, lang_code, category_version_numbers)

Delete multiple category versions

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.bulk_delete_category_version_response import BulkDeleteCategoryVersionResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the Category
    lang_code = 'lang_code_example' # str | Language code of the category
    category_version_numbers = [56] # List[int] | Array of category version numbers to be deleted

    try:
        # Delete multiple category versions
        api_response = await api_instance.v2_categories_bulkdelete_category_versions_delete(category_id, lang_code, category_version_numbers)
        print("The response of CategoriesApi->v2_categories_bulkdelete_category_versions_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_bulkdelete_category_versions_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the Category | 
 **lang_code** | **str**| Language code of the category | 
 **category_version_numbers** | [**List[int]**](int.md)| Array of category version numbers to be deleted | 

### Return type

[**BulkDeleteCategoryVersionResponse**](BulkDeleteCategoryVersionResponse.md)

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

# **v2_categories_bulkpublish_lang_code_post**
> BulkPublishCategoryResponse v2_categories_bulkpublish_lang_code_post(lang_code, bulk_publish_category=bulk_publish_category)

Publishes multiple categories

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.bulk_publish_category import BulkPublishCategory
from d361api.models.bulk_publish_category_response import BulkPublishCategoryResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    lang_code = 'en' # str | Language code of the category (default to 'en')
    bulk_publish_category = [{"category_id":"152e9239-1a5a-4044-b5de-1030f49976b6s","user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","version_number":1,"publish_message":"Publish Success"},{"category_id":"gr32e9239-1a5a-4044-b5de-1030f499fe6sr","user_id":"edr1efc6f-e968-4e95-82eb-ccad61559deef3","version_number":1,"publish_message":"Publish Success"}] # List[BulkPublishCategory] |  (optional)

    try:
        # Publishes multiple categories
        api_response = await api_instance.v2_categories_bulkpublish_lang_code_post(lang_code, bulk_publish_category=bulk_publish_category)
        print("The response of CategoriesApi->v2_categories_bulkpublish_lang_code_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_bulkpublish_lang_code_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lang_code** | **str**| Language code of the category | [default to &#39;en&#39;]
 **bulk_publish_category** | [**List[BulkPublishCategory]**](BulkPublishCategory.md)|  | [optional] 

### Return type

[**BulkPublishCategoryResponse**](BulkPublishCategoryResponse.md)

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

# **v2_categories_bulkupdate_content_put**
> BulkUpdateCategoryContentResponse v2_categories_bulkupdate_content_put(update_category_content_request=update_category_content_request)

Update multiple page categories

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.bulk_update_category_content_response import BulkUpdateCategoryContentResponse
from d361api.models.update_category_content_request import UpdateCategoryContentRequest
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
    api_instance = d361api.CategoriesApi(api_client)
    update_category_content_request = [{"category_id":"152e9239-1a5a-4044-b5de-1030f49976b6","lang_code":"en","title":"New Name","content":"No new content","html_content":"<p>No new content</p>","block_content":"<p>No new content</p>","version_number":2,"translation_option":null,"source":null,"updated_by":"f11efc6f-e968-4e95-82eb-85ad61559de8"}] # List[UpdateCategoryContentRequest] |  (optional)

    try:
        # Update multiple page categories
        api_response = await api_instance.v2_categories_bulkupdate_content_put(update_category_content_request=update_category_content_request)
        print("The response of CategoriesApi->v2_categories_bulkupdate_content_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_bulkupdate_content_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **update_category_content_request** | [**List[UpdateCategoryContentRequest]**](UpdateCategoryContentRequest.md)|  | [optional] 

### Return type

[**BulkUpdateCategoryContentResponse**](BulkUpdateCategoryContentResponse.md)

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

# **v2_categories_category_id_content_lang_code_get**
> GetCategoryContentResponse v2_categories_category_id_content_lang_code_get(category_id, lang_code, is_for_display=is_for_display, is_published=is_published, append_sas_token=append_sas_token)

Get category page with an ID

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_category_content_response import GetCategoryContentResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    lang_code = 'en' # str | Language code of the category (default to 'en')
    is_for_display = False # bool | Set this to true, if you are displaying the category to the end-user. If **true**, the content of snippets or variables appears in the category. Note: If the value is true, ensure that the article content is not passed for *update* category endpoints. (optional) (default to False)
    is_published = False # bool | To get latest published article, **set isPublished as true.** (optional) (default to False)
    append_sas_token = True # bool | Set this to false to exclude appending SAS token for images/files (optional) (default to True)

    try:
        # Get category page with an ID
        api_response = await api_instance.v2_categories_category_id_content_lang_code_get(category_id, lang_code, is_for_display=is_for_display, is_published=is_published, append_sas_token=append_sas_token)
        print("The response of CategoriesApi->v2_categories_category_id_content_lang_code_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_content_lang_code_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **lang_code** | **str**| Language code of the category | [default to &#39;en&#39;]
 **is_for_display** | **bool**| Set this to true, if you are displaying the category to the end-user. If **true**, the content of snippets or variables appears in the category. Note: If the value is true, ensure that the article content is not passed for *update* category endpoints. | [optional] [default to False]
 **is_published** | **bool**| To get latest published article, **set isPublished as true.** | [optional] [default to False]
 **append_sas_token** | **bool**| Set this to false to exclude appending SAS token for images/files | [optional] [default to True]

### Return type

[**GetCategoryContentResponse**](GetCategoryContentResponse.md)

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

# **v2_categories_category_id_content_lang_code_put**
> UpdateCategoryContentCustomerResponse v2_categories_category_id_content_lang_code_put(category_id, lang_code, update_category_content_customer_request=update_category_content_customer_request)

Update a category page content with the ID

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.update_category_content_customer_request import UpdateCategoryContentCustomerRequest
from d361api.models.update_category_content_customer_response import UpdateCategoryContentCustomerResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    lang_code = 'en' # str | Language code of the category (default to 'en')
    update_category_content_customer_request = {"title":"UpdateTitleForCategoryPage","content":"This is my updated content.","html_content":"<p>This is my updated content,</p>","block_content":"<p>This is my updated content,</p>","version_number":1,"translation_option":"","source":"","updated_by":"f11efc6f-e968-4e95-82eb-85ad61559de8"} # UpdateCategoryContentCustomerRequest |  (optional)

    try:
        # Update a category page content with the ID
        api_response = await api_instance.v2_categories_category_id_content_lang_code_put(category_id, lang_code, update_category_content_customer_request=update_category_content_customer_request)
        print("The response of CategoriesApi->v2_categories_category_id_content_lang_code_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_content_lang_code_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **lang_code** | **str**| Language code of the category | [default to &#39;en&#39;]
 **update_category_content_customer_request** | [**UpdateCategoryContentCustomerRequest**](UpdateCategoryContentCustomerRequest.md)|  | [optional] 

### Return type

[**UpdateCategoryContentCustomerResponse**](UpdateCategoryContentCustomerResponse.md)

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

# **v2_categories_category_id_delete**
> CustomerApiBaseResponse v2_categories_category_id_delete(category_id)

Deletes an category with an ID

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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category

    try:
        # Deletes an category with an ID
        api_response = await api_instance.v2_categories_category_id_delete(category_id)
        print("The response of CategoriesApi->v2_categories_category_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 

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

# **v2_categories_category_id_fork_put**
> ForkCategoryVersionResponse v2_categories_category_id_fork_put(category_id, fork_category_version_request=fork_category_version_request)

Fork category page with an id

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.fork_category_version_request import ForkCategoryVersionRequest
from d361api.models.fork_category_version_response import ForkCategoryVersionResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | ID of the category
    fork_category_version_request = {"version_number":1,"user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","lang_code":"en"} # ForkCategoryVersionRequest |  (optional)

    try:
        # Fork category page with an id
        api_response = await api_instance.v2_categories_category_id_fork_put(category_id, fork_category_version_request=fork_category_version_request)
        print("The response of CategoriesApi->v2_categories_category_id_fork_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_fork_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| ID of the category | 
 **fork_category_version_request** | [**ForkCategoryVersionRequest**](ForkCategoryVersionRequest.md)|  | [optional] 

### Return type

[**ForkCategoryVersionResponse**](ForkCategoryVersionResponse.md)

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

# **v2_categories_category_id_get**
> GetCategoryResponse v2_categories_category_id_get(category_id, lang_code=lang_code)

Get category with an ID

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_category_response import GetCategoryResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    lang_code = 'lang_code_example' # str | If the language code is empty, the default language of the category will be taken into account. (optional)

    try:
        # Get category with an ID
        api_response = await api_instance.v2_categories_category_id_get(category_id, lang_code=lang_code)
        print("The response of CategoriesApi->v2_categories_category_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **lang_code** | **str**| If the language code is empty, the default language of the category will be taken into account. | [optional] 

### Return type

[**GetCategoryResponse**](GetCategoryResponse.md)

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

# **v2_categories_category_id_lang_code_publish_post**
> BulkCreateCategoryResponse v2_categories_category_id_lang_code_publish_post(category_id, lang_code, publish_category_request=publish_category_request)

Publishes an category with an id

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.bulk_create_category_response import BulkCreateCategoryResponse
from d361api.models.publish_category_request import PublishCategoryRequest
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    lang_code = 'en' # str | Language code of the category (default to 'en')
    publish_category_request = {"user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","version_number":1,"publish_message":"Successfully Published"} # PublishCategoryRequest |  (optional)

    try:
        # Publishes an category with an id
        api_response = await api_instance.v2_categories_category_id_lang_code_publish_post(category_id, lang_code, publish_category_request=publish_category_request)
        print("The response of CategoriesApi->v2_categories_category_id_lang_code_publish_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_lang_code_publish_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **lang_code** | **str**| Language code of the category | [default to &#39;en&#39;]
 **publish_category_request** | [**PublishCategoryRequest**](PublishCategoryRequest.md)|  | [optional] 

### Return type

[**BulkCreateCategoryResponse**](BulkCreateCategoryResponse.md)

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

# **v2_categories_category_id_lang_code_settings_get**
> GetCategorySettingsResponse v2_categories_category_id_lang_code_settings_get(category_id, lang_code)

Get settings for the Category

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_category_settings_response import GetCategorySettingsResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    lang_code = 'en' # str | Language code of the category (default to 'en')

    try:
        # Get settings for the Category
        api_response = await api_instance.v2_categories_category_id_lang_code_settings_get(category_id, lang_code)
        print("The response of CategoriesApi->v2_categories_category_id_lang_code_settings_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_lang_code_settings_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **lang_code** | **str**| Language code of the category | [default to &#39;en&#39;]

### Return type

[**GetCategorySettingsResponse**](GetCategorySettingsResponse.md)

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

# **v2_categories_category_id_lang_code_settings_put**
> GetCategorySettingsResponse v2_categories_category_id_lang_code_settings_put(category_id, lang_code, update_article_settings_request=update_article_settings_request)

Update settings for the category

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_category_settings_response import GetCategorySettingsResponse
from d361api.models.update_article_settings_request import UpdateArticleSettingsRequest
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    lang_code = 'en' # str | Language code of the category (default to 'en')
    update_article_settings_request = {"slug":"updatedslug","seo_title":"updatedSeoTitle","description":"This is the description in updating category settings.","allow_comments":true,"show_table_of_contents":true,"tags":[],"status_indicator":1,"status_indicator_expiry_date":"2024-06-13T14:30:00","exclude_from_search":true,"exclude_from_ai_search":false,"related_articles":[],"content_type":0,"is_acknowledgement_enabled":false} # UpdateArticleSettingsRequest |  (optional)

    try:
        # Update settings for the category
        api_response = await api_instance.v2_categories_category_id_lang_code_settings_put(category_id, lang_code, update_article_settings_request=update_article_settings_request)
        print("The response of CategoriesApi->v2_categories_category_id_lang_code_settings_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_lang_code_settings_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **lang_code** | **str**| Language code of the category | [default to &#39;en&#39;]
 **update_article_settings_request** | [**UpdateArticleSettingsRequest**](UpdateArticleSettingsRequest.md)|  | [optional] 

### Return type

[**GetCategorySettingsResponse**](GetCategorySettingsResponse.md)

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

# **v2_categories_category_id_lang_code_update_description_put**
> CustomerApiBaseResponse v2_categories_category_id_lang_code_update_description_put(category_id, lang_code, description=description)

Update the category description

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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    lang_code = 'en' # str | Language code of the category (default to 'en')
    description = 'description_example' # str | The description of the category (optional)

    try:
        # Update the category description
        api_response = await api_instance.v2_categories_category_id_lang_code_update_description_put(category_id, lang_code, description=description)
        print("The response of CategoriesApi->v2_categories_category_id_lang_code_update_description_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_lang_code_update_description_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **lang_code** | **str**| Language code of the category | [default to &#39;en&#39;]
 **description** | **str**| The description of the category | [optional] 

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

# **v2_categories_category_id_lang_code_version_version_number_delete**
> CustomerApiBaseResponse v2_categories_category_id_lang_code_version_version_number_delete(category_id, version_number, lang_code)

Delete category Version

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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    version_number = 56 # int | Version number of the category to be deleted
    lang_code = 'en' # str | Language code of the category (default to 'en')

    try:
        # Delete category Version
        api_response = await api_instance.v2_categories_category_id_lang_code_version_version_number_delete(category_id, version_number, lang_code)
        print("The response of CategoriesApi->v2_categories_category_id_lang_code_version_version_number_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_lang_code_version_version_number_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **version_number** | **int**| Version number of the category to be deleted | 
 **lang_code** | **str**| Language code of the category | [default to &#39;en&#39;]

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

# **v2_categories_category_id_lang_codeversions_get**
> GetCategoryVersionsResponse v2_categories_category_id_lang_codeversions_get(category_id, lang_code)

Get category page versions

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_category_versions_response import GetCategoryVersionsResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    lang_code = 'en' # str | Language code of the category (default to 'en')

    try:
        # Get category page versions
        api_response = await api_instance.v2_categories_category_id_lang_codeversions_get(category_id, lang_code)
        print("The response of CategoriesApi->v2_categories_category_id_lang_codeversions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_lang_codeversions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **lang_code** | **str**| Language code of the category | [default to &#39;en&#39;]

### Return type

[**GetCategoryVersionsResponse**](GetCategoryVersionsResponse.md)

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

# **v2_categories_category_id_publish_post**
> BulkCreateCategoryResponse v2_categories_category_id_publish_post(category_id, publish_category_request=publish_category_request)

Publishes an category with an id

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.bulk_create_category_response import BulkCreateCategoryResponse
from d361api.models.publish_category_request import PublishCategoryRequest
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    publish_category_request = {"user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","version_number":1,"publish_message":"Successfully Published"} # PublishCategoryRequest |  (optional)

    try:
        # Publishes an category with an id
        api_response = await api_instance.v2_categories_category_id_publish_post(category_id, publish_category_request=publish_category_request)
        print("The response of CategoriesApi->v2_categories_category_id_publish_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_publish_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **publish_category_request** | [**PublishCategoryRequest**](PublishCategoryRequest.md)|  | [optional] 

### Return type

[**BulkCreateCategoryResponse**](BulkCreateCategoryResponse.md)

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

# **v2_categories_category_id_put**
> UpdateCategoryResponse v2_categories_category_id_put(category_id, update_category_request=update_category_request)

Update a category with the ID

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.update_category_request import UpdateCategoryRequest
from d361api.models.update_category_response import UpdateCategoryResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    update_category_request = {"name":"UpdatedName","order":0,"parent_category_id":"814bd3cc-4cd1-4f97-adde-d4d644e9fe78","hidden":false,"icon":"","language":"en"} # UpdateCategoryRequest |  (optional)

    try:
        # Update a category with the ID
        api_response = await api_instance.v2_categories_category_id_put(category_id, update_category_request=update_category_request)
        print("The response of CategoriesApi->v2_categories_category_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **update_category_request** | [**UpdateCategoryRequest**](UpdateCategoryRequest.md)|  | [optional] 

### Return type

[**UpdateCategoryResponse**](UpdateCategoryResponse.md)

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

# **v2_categories_category_id_settings_get**
> GetCategorySettingsResponse v2_categories_category_id_settings_get(category_id)

Get settings for the Category

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_category_settings_response import GetCategorySettingsResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category

    try:
        # Get settings for the Category
        api_response = await api_instance.v2_categories_category_id_settings_get(category_id)
        print("The response of CategoriesApi->v2_categories_category_id_settings_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_settings_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 

### Return type

[**GetCategorySettingsResponse**](GetCategorySettingsResponse.md)

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

# **v2_categories_category_id_settings_put**
> GetCategorySettingsResponse v2_categories_category_id_settings_put(category_id, update_article_settings_request=update_article_settings_request)

Update settings for the category

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_category_settings_response import GetCategorySettingsResponse
from d361api.models.update_article_settings_request import UpdateArticleSettingsRequest
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    update_article_settings_request = {"slug":"updatedslug","seo_title":"updatedSeoTitle","description":"This is the description in updating category settings.","allow_comments":true,"show_table_of_contents":true,"tags":[],"status_indicator":1,"status_indicator_expiry_date":"2024-06-13T14:30:00","exclude_from_search":true,"exclude_from_ai_search":false,"related_articles":[],"content_type":0,"is_acknowledgement_enabled":false} # UpdateArticleSettingsRequest |  (optional)

    try:
        # Update settings for the category
        api_response = await api_instance.v2_categories_category_id_settings_put(category_id, update_article_settings_request=update_article_settings_request)
        print("The response of CategoriesApi->v2_categories_category_id_settings_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_settings_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **update_article_settings_request** | [**UpdateArticleSettingsRequest**](UpdateArticleSettingsRequest.md)|  | [optional] 

### Return type

[**GetCategorySettingsResponse**](GetCategorySettingsResponse.md)

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

# **v2_categories_category_id_update_category_type_put**
> CustomerApiBaseResponse v2_categories_category_id_update_category_type_put(category_id, category_type, user_id)

Update the Category Type

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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    category_type = d361api.CategoryType() # CategoryType | Category type (0-Folder, 1-Page, 2-Index)
    user_id = 'user_id_example' # str | The ID of the team account

    try:
        # Update the Category Type
        api_response = await api_instance.v2_categories_category_id_update_category_type_put(category_id, category_type, user_id)
        print("The response of CategoriesApi->v2_categories_category_id_update_category_type_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_update_category_type_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **category_type** | [**CategoryType**](.md)| Category type (0-Folder, 1-Page, 2-Index) | 
 **user_id** | **str**| The ID of the team account | 

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

# **v2_categories_category_id_update_description_put**
> CustomerApiBaseResponse v2_categories_category_id_update_description_put(category_id, description=description)

Update the category description

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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    description = 'description_example' # str | The description of the category (optional)

    try:
        # Update the category description
        api_response = await api_instance.v2_categories_category_id_update_description_put(category_id, description=description)
        print("The response of CategoriesApi->v2_categories_category_id_update_description_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_update_description_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **description** | **str**| The description of the category | [optional] 

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

# **v2_categories_category_id_version_version_number_delete**
> CustomerApiBaseResponse v2_categories_category_id_version_version_number_delete(category_id, version_number)

Delete category Version

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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    version_number = 56 # int | Version number of the category to be deleted

    try:
        # Delete category Version
        api_response = await api_instance.v2_categories_category_id_version_version_number_delete(category_id, version_number)
        print("The response of CategoriesApi->v2_categories_category_id_version_version_number_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_version_version_number_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **version_number** | **int**| Version number of the category to be deleted | 

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

# **v2_categories_category_id_versions_get**
> GetCategoryVersionsResponse v2_categories_category_id_versions_get(category_id)

Get category page versions

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_category_versions_response import GetCategoryVersionsResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category

    try:
        # Get category page versions
        api_response = await api_instance.v2_categories_category_id_versions_get(category_id)
        print("The response of CategoriesApi->v2_categories_category_id_versions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_versions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 

### Return type

[**GetCategoryVersionsResponse**](GetCategoryVersionsResponse.md)

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

# **v2_categories_category_id_versions_lang_code_version_number_get**
> GetCategoryContentResponse v2_categories_category_id_versions_lang_code_version_number_get(category_id, version_number, lang_code, is_for_display=is_for_display, append_sas_token=append_sas_token)

Get category page content with an ID

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_category_content_response import GetCategoryContentResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    version_number = 56 # int | Version number of the category
    lang_code = 'en' # str | Language code of the category (default to 'en')
    is_for_display = False # bool | Set this to true, if you are displaying the category to the end-user. If true, the content of snippets or variables appears in the category. Note: If the value is true, ensure that the category content is not passed for update category endpoints. (optional) (default to False)
    append_sas_token = True # bool | Set this to false to exclude appending SAS token for images/files (optional) (default to True)

    try:
        # Get category page content with an ID
        api_response = await api_instance.v2_categories_category_id_versions_lang_code_version_number_get(category_id, version_number, lang_code, is_for_display=is_for_display, append_sas_token=append_sas_token)
        print("The response of CategoriesApi->v2_categories_category_id_versions_lang_code_version_number_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_versions_lang_code_version_number_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **version_number** | **int**| Version number of the category | 
 **lang_code** | **str**| Language code of the category | [default to &#39;en&#39;]
 **is_for_display** | **bool**| Set this to true, if you are displaying the category to the end-user. If true, the content of snippets or variables appears in the category. Note: If the value is true, ensure that the category content is not passed for update category endpoints. | [optional] [default to False]
 **append_sas_token** | **bool**| Set this to false to exclude appending SAS token for images/files | [optional] [default to True]

### Return type

[**GetCategoryContentResponse**](GetCategoryContentResponse.md)

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

# **v2_categories_category_id_versions_version_number_get**
> GetCategoryContentResponse v2_categories_category_id_versions_version_number_get(category_id, version_number, is_for_display=is_for_display, append_sas_token=append_sas_token)

Get category page content with an ID

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_category_content_response import GetCategoryContentResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    category_id = 'category_id_example' # str | The ID of the category
    version_number = 56 # int | Version number of the category
    is_for_display = False # bool | Set this to true, if you are displaying the category to the end-user. If true, the content of snippets or variables appears in the category. Note: If the value is true, ensure that the category content is not passed for update category endpoints. (optional) (default to False)
    append_sas_token = True # bool | Set this to false to exclude appending SAS token for images/files (optional) (default to True)

    try:
        # Get category page content with an ID
        api_response = await api_instance.v2_categories_category_id_versions_version_number_get(category_id, version_number, is_for_display=is_for_display, append_sas_token=append_sas_token)
        print("The response of CategoriesApi->v2_categories_category_id_versions_version_number_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_category_id_versions_version_number_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**| The ID of the category | 
 **version_number** | **int**| Version number of the category | 
 **is_for_display** | **bool**| Set this to true, if you are displaying the category to the end-user. If true, the content of snippets or variables appears in the category. Note: If the value is true, ensure that the category content is not passed for update category endpoints. | [optional] [default to False]
 **append_sas_token** | **bool**| Set this to false to exclude appending SAS token for images/files | [optional] [default to True]

### Return type

[**GetCategoryContentResponse**](GetCategoryContentResponse.md)

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

# **v2_categories_post**
> AddCategoryResponse v2_categories_post(add_category_request=add_category_request)

Adds a new category

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.add_category_request import AddCategoryRequest
from d361api.models.add_category_response import AddCategoryResponse
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
    api_instance = d361api.CategoriesApi(api_client)
    add_category_request = {"name":"New Category","project_version_id":"46f48bc7-760f-4b07-b2d2-fce4aa8ba234","order":0,"parent_category_id":null,"content":null,"category_type":0,"user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","content_type":null} # AddCategoryRequest |  (optional)

    try:
        # Adds a new category
        api_response = await api_instance.v2_categories_post(add_category_request=add_category_request)
        print("The response of CategoriesApi->v2_categories_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->v2_categories_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **add_category_request** | [**AddCategoryRequest**](AddCategoryRequest.md)|  | [optional] 

### Return type

[**AddCategoryResponse**](AddCategoryResponse.md)

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

