# d361api.ArticlesApi

All URIs are relative to *https://apihub.document360.io*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_articles_article_id_delete**](ArticlesApi.md#v2_articles_article_id_delete) | **DELETE** /v2/Articles/{articleId} | Deletes an article with an ID
[**v2_articles_article_id_fork_put**](ArticlesApi.md#v2_articles_article_id_fork_put) | **PUT** /v2/Articles/{articleId}/fork | Forks an article with an id
[**v2_articles_article_id_lang_code_get**](ArticlesApi.md#v2_articles_article_id_lang_code_get) | **GET** /v2/Articles/{articleId}/{langCode} | Gets an article
[**v2_articles_article_id_lang_code_publish_post**](ArticlesApi.md#v2_articles_article_id_lang_code_publish_post) | **POST** /v2/Articles/{articleId}/{langCode}/publish | Publishes an article with an id
[**v2_articles_article_id_lang_code_put**](ArticlesApi.md#v2_articles_article_id_lang_code_put) | **PUT** /v2/Articles/{articleId}/{langCode} | Updates an article with the ID
[**v2_articles_article_id_lang_code_settings_get**](ArticlesApi.md#v2_articles_article_id_lang_code_settings_get) | **GET** /v2/Articles/{articleId}/{langCode}/settings | Gets settings for the article
[**v2_articles_article_id_lang_code_settings_put**](ArticlesApi.md#v2_articles_article_id_lang_code_settings_put) | **PUT** /v2/Articles/{articleId}/{langCode}/settings | Updates settings for the article
[**v2_articles_article_id_lang_code_update_description_put**](ArticlesApi.md#v2_articles_article_id_lang_code_update_description_put) | **PUT** /v2/Articles/{articleId}/{langCode}/updateDescription | Update the Article Description
[**v2_articles_article_id_lang_code_version_version_number_delete**](ArticlesApi.md#v2_articles_article_id_lang_code_version_version_number_delete) | **DELETE** /v2/Articles/{articleId}/{langCode}/version/{versionNumber} | Deletes an article version
[**v2_articles_article_id_lang_code_versions_get**](ArticlesApi.md#v2_articles_article_id_lang_code_versions_get) | **GET** /v2/Articles/{articleId}/{langCode}/versions | Gets all article versions
[**v2_articles_article_id_lang_code_versions_version_number_get**](ArticlesApi.md#v2_articles_article_id_lang_code_versions_version_number_get) | **GET** /v2/Articles/{articleId}/{langCode}/versions/{versionNumber} | Gets article by a version number
[**v2_articles_article_id_publish_post**](ArticlesApi.md#v2_articles_article_id_publish_post) | **POST** /v2/Articles/{articleId}/publish | Publishes an article with an id
[**v2_articles_article_id_settings_get**](ArticlesApi.md#v2_articles_article_id_settings_get) | **GET** /v2/Articles/{articleId}/settings | Gets settings for the article
[**v2_articles_article_id_settings_put**](ArticlesApi.md#v2_articles_article_id_settings_put) | **PUT** /v2/Articles/{articleId}/settings | Updates settings for the article
[**v2_articles_article_id_update_description_put**](ArticlesApi.md#v2_articles_article_id_update_description_put) | **PUT** /v2/Articles/{articleId}/updateDescription | Update the Article Description
[**v2_articles_article_id_version_version_number_delete**](ArticlesApi.md#v2_articles_article_id_version_version_number_delete) | **DELETE** /v2/Articles/{articleId}/version/{versionNumber} | Deletes an article version
[**v2_articles_article_id_versions_get**](ArticlesApi.md#v2_articles_article_id_versions_get) | **GET** /v2/Articles/{articleId}/versions | Gets all article versions
[**v2_articles_article_id_versions_version_number_get**](ArticlesApi.md#v2_articles_article_id_versions_version_number_get) | **GET** /v2/Articles/{articleId}/versions/{versionNumber} | Gets article by a version number
[**v2_articles_bulkcreate_post**](ArticlesApi.md#v2_articles_bulkcreate_post) | **POST** /v2/Articles/bulkcreate | Adds multiple articles
[**v2_articles_bulkdelete_article_versions_delete**](ArticlesApi.md#v2_articles_bulkdelete_article_versions_delete) | **DELETE** /v2/Articles/bulkdelete-article-versions | Delete multiple article versions
[**v2_articles_bulkdelete_delete**](ArticlesApi.md#v2_articles_bulkdelete_delete) | **DELETE** /v2/Articles/bulkdelete | Deletes multiple articles
[**v2_articles_bulkpublish_lang_code_post**](ArticlesApi.md#v2_articles_bulkpublish_lang_code_post) | **POST** /v2/Articles/bulkpublish/{langCode} | Publishes multiple articles
[**v2_articles_bulkupdate_put**](ArticlesApi.md#v2_articles_bulkupdate_put) | **PUT** /v2/Articles/bulkupdate | Updates multiple articles
[**v2_articles_post**](ArticlesApi.md#v2_articles_post) | **POST** /v2/Articles | Adds an article to an existing category


# **v2_articles_article_id_delete**
> CustomerApiBaseResponse v2_articles_article_id_delete(article_id)

Deletes an article with an ID

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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article

    try:
        # Deletes an article with an ID
        api_response = await api_instance.v2_articles_article_id_delete(article_id)
        print("The response of ArticlesApi->v2_articles_article_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 

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

# **v2_articles_article_id_fork_put**
> ForkArticleVersionResponse v2_articles_article_id_fork_put(article_id, fork_article_version_request=fork_article_version_request)

Forks an article with an id

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.fork_article_version_request import ForkArticleVersionRequest
from d361api.models.fork_article_version_response import ForkArticleVersionResponse
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    fork_article_version_request = {"version_number":2,"user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","lang_code":"en"} # ForkArticleVersionRequest |  (optional)

    try:
        # Forks an article with an id
        api_response = await api_instance.v2_articles_article_id_fork_put(article_id, fork_article_version_request=fork_article_version_request)
        print("The response of ArticlesApi->v2_articles_article_id_fork_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_fork_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **fork_article_version_request** | [**ForkArticleVersionRequest**](ForkArticleVersionRequest.md)|  | [optional] 

### Return type

[**ForkArticleVersionResponse**](ForkArticleVersionResponse.md)

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

# **v2_articles_article_id_lang_code_get**
> GetArticleResponseCustomer v2_articles_article_id_lang_code_get(article_id, lang_code, is_for_display=is_for_display, is_published=is_published, append_sas_token=append_sas_token)

Gets an article

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_article_response_customer import GetArticleResponseCustomer
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    lang_code = 'en' # str | Language code of the article (default to 'en')
    is_for_display = False # bool | Set this to true, if you are displaying the article to the end-user. If true, the content of snippets or variables appears in the article. Note: If the value is true, ensure that the article content is not passed for update article endpoints. (optional) (default to False)
    is_published = False # bool | **true** : You will get the latest published version of the article. (If there are no published versions, then it will return the latest version)              **false** : To get the the latest version of the article (optional) (default to False)
    append_sas_token = True # bool | Set this to false to exclude appending SAS token for images/files (optional) (default to True)

    try:
        # Gets an article
        api_response = await api_instance.v2_articles_article_id_lang_code_get(article_id, lang_code, is_for_display=is_for_display, is_published=is_published, append_sas_token=append_sas_token)
        print("The response of ArticlesApi->v2_articles_article_id_lang_code_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_lang_code_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **lang_code** | **str**| Language code of the article | [default to &#39;en&#39;]
 **is_for_display** | **bool**| Set this to true, if you are displaying the article to the end-user. If true, the content of snippets or variables appears in the article. Note: If the value is true, ensure that the article content is not passed for update article endpoints. | [optional] [default to False]
 **is_published** | **bool**| **true** : You will get the latest published version of the article. (If there are no published versions, then it will return the latest version)              **false** : To get the the latest version of the article | [optional] [default to False]
 **append_sas_token** | **bool**| Set this to false to exclude appending SAS token for images/files | [optional] [default to True]

### Return type

[**GetArticleResponseCustomer**](GetArticleResponseCustomer.md)

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

# **v2_articles_article_id_lang_code_publish_post**
> CreateArticleResponse v2_articles_article_id_lang_code_publish_post(article_id, lang_code, publish_article_request=publish_article_request)

Publishes an article with an id

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.create_article_response import CreateArticleResponse
from d361api.models.publish_article_request import PublishArticleRequest
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    lang_code = 'en' # str | Language code of the article (default to 'en')
    publish_article_request = {"user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","version_number":1,"publish_message":"Publishing my article with new changes."} # PublishArticleRequest |  (optional)

    try:
        # Publishes an article with an id
        api_response = await api_instance.v2_articles_article_id_lang_code_publish_post(article_id, lang_code, publish_article_request=publish_article_request)
        print("The response of ArticlesApi->v2_articles_article_id_lang_code_publish_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_lang_code_publish_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **lang_code** | **str**| Language code of the article | [default to &#39;en&#39;]
 **publish_article_request** | [**PublishArticleRequest**](PublishArticleRequest.md)|  | [optional] 

### Return type

[**CreateArticleResponse**](CreateArticleResponse.md)

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

# **v2_articles_article_id_lang_code_put**
> CreateArticleResponse v2_articles_article_id_lang_code_put(article_id, lang_code, update_article_request=update_article_request)

Updates an article with the ID

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.create_article_response import CreateArticleResponse
from d361api.models.update_article_request import UpdateArticleRequest
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    lang_code = 'en' # str | Language code of the article (default to 'en')
    update_article_request = {"title":"updated article title","content":"Hi this is an API article Sample. This is updated.","html_content":"<p>Hi this is an API article Sample. This is updated.</p>","category_id":"5b291e6b-fa40-4ab9-941e-f8fffc23b376","hidden":true,"version_number":1,"translation_option":"0","source":"uat","order":0} # UpdateArticleRequest |  (optional)

    try:
        # Updates an article with the ID
        api_response = await api_instance.v2_articles_article_id_lang_code_put(article_id, lang_code, update_article_request=update_article_request)
        print("The response of ArticlesApi->v2_articles_article_id_lang_code_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_lang_code_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **lang_code** | **str**| Language code of the article | [default to &#39;en&#39;]
 **update_article_request** | [**UpdateArticleRequest**](UpdateArticleRequest.md)|  | [optional] 

### Return type

[**CreateArticleResponse**](CreateArticleResponse.md)

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

# **v2_articles_article_id_lang_code_settings_get**
> GetArticleSettingsResponse v2_articles_article_id_lang_code_settings_get(article_id, lang_code)

Gets settings for the article

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_article_settings_response import GetArticleSettingsResponse
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    lang_code = 'en' # str | Language code of the article (default to 'en')

    try:
        # Gets settings for the article
        api_response = await api_instance.v2_articles_article_id_lang_code_settings_get(article_id, lang_code)
        print("The response of ArticlesApi->v2_articles_article_id_lang_code_settings_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_lang_code_settings_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **lang_code** | **str**| Language code of the article | [default to &#39;en&#39;]

### Return type

[**GetArticleSettingsResponse**](GetArticleSettingsResponse.md)

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

# **v2_articles_article_id_lang_code_settings_put**
> UpdateArticleSettingsResponseCustomer v2_articles_article_id_lang_code_settings_put(article_id, lang_code, update_article_settings_request=update_article_settings_request)

Updates settings for the article

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.update_article_settings_request import UpdateArticleSettingsRequest
from d361api.models.update_article_settings_response_customer import UpdateArticleSettingsResponseCustomer
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    lang_code = 'en' # str | Language code of the article (default to 'en')
    update_article_settings_request = {"slug":"updatearticlesettings","seo_title":"update","description":"This is the description for updating article settings.","allow_comments":true,"show_table_of_contents":true,"tags":[],"status_indicator":2,"status_indicator_expiry_date":"2024-06-13T14:30:00","exclude_from_search":true,"exclude_from_ai_search":false,"related_articles":[],"content_type":0,"is_acknowledgement_enabled":false} # UpdateArticleSettingsRequest |  (optional)

    try:
        # Updates settings for the article
        api_response = await api_instance.v2_articles_article_id_lang_code_settings_put(article_id, lang_code, update_article_settings_request=update_article_settings_request)
        print("The response of ArticlesApi->v2_articles_article_id_lang_code_settings_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_lang_code_settings_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **lang_code** | **str**| Language code of the article | [default to &#39;en&#39;]
 **update_article_settings_request** | [**UpdateArticleSettingsRequest**](UpdateArticleSettingsRequest.md)|  | [optional] 

### Return type

[**UpdateArticleSettingsResponseCustomer**](UpdateArticleSettingsResponseCustomer.md)

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

# **v2_articles_article_id_lang_code_update_description_put**
> CustomerApiBaseResponse v2_articles_article_id_lang_code_update_description_put(article_id, lang_code, description=description)

Update the Article Description

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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    lang_code = 'en' # str | Language code of the article (default to 'en')
    description = 'description_example' # str | The description of the article (optional)

    try:
        # Update the Article Description
        api_response = await api_instance.v2_articles_article_id_lang_code_update_description_put(article_id, lang_code, description=description)
        print("The response of ArticlesApi->v2_articles_article_id_lang_code_update_description_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_lang_code_update_description_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **lang_code** | **str**| Language code of the article | [default to &#39;en&#39;]
 **description** | **str**| The description of the article | [optional] 

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

# **v2_articles_article_id_lang_code_version_version_number_delete**
> CustomerApiBaseResponse v2_articles_article_id_lang_code_version_version_number_delete(article_id, version_number, lang_code)

Deletes an article version

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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    version_number = 56 # int | Version number of the article
    lang_code = 'en' # str | Language code of the article (default to 'en')

    try:
        # Deletes an article version
        api_response = await api_instance.v2_articles_article_id_lang_code_version_version_number_delete(article_id, version_number, lang_code)
        print("The response of ArticlesApi->v2_articles_article_id_lang_code_version_version_number_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_lang_code_version_version_number_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **version_number** | **int**| Version number of the article | 
 **lang_code** | **str**| Language code of the article | [default to &#39;en&#39;]

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

# **v2_articles_article_id_lang_code_versions_get**
> GetArticleVersionsResponse v2_articles_article_id_lang_code_versions_get(article_id, lang_code)

Gets all article versions

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_article_versions_response import GetArticleVersionsResponse
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    lang_code = 'en' # str |  (default to 'en')

    try:
        # Gets all article versions
        api_response = await api_instance.v2_articles_article_id_lang_code_versions_get(article_id, lang_code)
        print("The response of ArticlesApi->v2_articles_article_id_lang_code_versions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_lang_code_versions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **lang_code** | **str**|  | [default to &#39;en&#39;]

### Return type

[**GetArticleVersionsResponse**](GetArticleVersionsResponse.md)

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

# **v2_articles_article_id_lang_code_versions_version_number_get**
> GetArticleVersionResponse v2_articles_article_id_lang_code_versions_version_number_get(article_id, version_number, lang_code, is_for_display=is_for_display, append_sas_token=append_sas_token)

Gets article by a version number

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_article_version_response import GetArticleVersionResponse
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    version_number = 56 # int | Version number of the article
    lang_code = 'en' # str | Language code of the article (default to 'en')
    is_for_display = False # bool | Set this to true, if you are displaying the article to the end-user. If true, the content of snippets or variables appears in the article. Note: If the value is true, ensure that the article content is not passed for update article endpoints. (optional) (default to False)
    append_sas_token = True # bool | Set this to false to exclude appending SAS token for images/files (optional) (default to True)

    try:
        # Gets article by a version number
        api_response = await api_instance.v2_articles_article_id_lang_code_versions_version_number_get(article_id, version_number, lang_code, is_for_display=is_for_display, append_sas_token=append_sas_token)
        print("The response of ArticlesApi->v2_articles_article_id_lang_code_versions_version_number_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_lang_code_versions_version_number_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **version_number** | **int**| Version number of the article | 
 **lang_code** | **str**| Language code of the article | [default to &#39;en&#39;]
 **is_for_display** | **bool**| Set this to true, if you are displaying the article to the end-user. If true, the content of snippets or variables appears in the article. Note: If the value is true, ensure that the article content is not passed for update article endpoints. | [optional] [default to False]
 **append_sas_token** | **bool**| Set this to false to exclude appending SAS token for images/files | [optional] [default to True]

### Return type

[**GetArticleVersionResponse**](GetArticleVersionResponse.md)

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

# **v2_articles_article_id_publish_post**
> CreateArticleResponse v2_articles_article_id_publish_post(article_id, publish_article_request=publish_article_request)

Publishes an article with an id

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.create_article_response import CreateArticleResponse
from d361api.models.publish_article_request import PublishArticleRequest
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    publish_article_request = {"user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","version_number":1,"publish_message":"Publishing my article with new changes."} # PublishArticleRequest |  (optional)

    try:
        # Publishes an article with an id
        api_response = await api_instance.v2_articles_article_id_publish_post(article_id, publish_article_request=publish_article_request)
        print("The response of ArticlesApi->v2_articles_article_id_publish_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_publish_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **publish_article_request** | [**PublishArticleRequest**](PublishArticleRequest.md)|  | [optional] 

### Return type

[**CreateArticleResponse**](CreateArticleResponse.md)

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

# **v2_articles_article_id_settings_get**
> GetArticleSettingsResponse v2_articles_article_id_settings_get(article_id)

Gets settings for the article

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_article_settings_response import GetArticleSettingsResponse
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article

    try:
        # Gets settings for the article
        api_response = await api_instance.v2_articles_article_id_settings_get(article_id)
        print("The response of ArticlesApi->v2_articles_article_id_settings_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_settings_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 

### Return type

[**GetArticleSettingsResponse**](GetArticleSettingsResponse.md)

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

# **v2_articles_article_id_settings_put**
> UpdateArticleSettingsResponseCustomer v2_articles_article_id_settings_put(article_id, update_article_settings_request=update_article_settings_request)

Updates settings for the article

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.update_article_settings_request import UpdateArticleSettingsRequest
from d361api.models.update_article_settings_response_customer import UpdateArticleSettingsResponseCustomer
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    update_article_settings_request = {"slug":"updatearticlesettings","seo_title":"update","description":"This is the description for updating article settings.","allow_comments":true,"show_table_of_contents":true,"tags":[],"status_indicator":2,"status_indicator_expiry_date":"2024-06-13T14:30:00","exclude_from_search":true,"exclude_from_ai_search":false,"related_articles":[],"content_type":0,"is_acknowledgement_enabled":false} # UpdateArticleSettingsRequest |  (optional)

    try:
        # Updates settings for the article
        api_response = await api_instance.v2_articles_article_id_settings_put(article_id, update_article_settings_request=update_article_settings_request)
        print("The response of ArticlesApi->v2_articles_article_id_settings_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_settings_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **update_article_settings_request** | [**UpdateArticleSettingsRequest**](UpdateArticleSettingsRequest.md)|  | [optional] 

### Return type

[**UpdateArticleSettingsResponseCustomer**](UpdateArticleSettingsResponseCustomer.md)

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

# **v2_articles_article_id_update_description_put**
> CustomerApiBaseResponse v2_articles_article_id_update_description_put(article_id, description=description)

Update the Article Description

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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    description = 'description_example' # str | The description of the article (optional)

    try:
        # Update the Article Description
        api_response = await api_instance.v2_articles_article_id_update_description_put(article_id, description=description)
        print("The response of ArticlesApi->v2_articles_article_id_update_description_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_update_description_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **description** | **str**| The description of the article | [optional] 

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

# **v2_articles_article_id_version_version_number_delete**
> CustomerApiBaseResponse v2_articles_article_id_version_version_number_delete(article_id, version_number)

Deletes an article version

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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    version_number = 56 # int | Version number of the article

    try:
        # Deletes an article version
        api_response = await api_instance.v2_articles_article_id_version_version_number_delete(article_id, version_number)
        print("The response of ArticlesApi->v2_articles_article_id_version_version_number_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_version_version_number_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **version_number** | **int**| Version number of the article | 

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

# **v2_articles_article_id_versions_get**
> GetArticleVersionsResponse v2_articles_article_id_versions_get(article_id)

Gets all article versions

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_article_versions_response import GetArticleVersionsResponse
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article

    try:
        # Gets all article versions
        api_response = await api_instance.v2_articles_article_id_versions_get(article_id)
        print("The response of ArticlesApi->v2_articles_article_id_versions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_versions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 

### Return type

[**GetArticleVersionsResponse**](GetArticleVersionsResponse.md)

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

# **v2_articles_article_id_versions_version_number_get**
> GetArticleVersionResponse v2_articles_article_id_versions_version_number_get(article_id, version_number, is_for_display=is_for_display, append_sas_token=append_sas_token)

Gets article by a version number

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_article_version_response import GetArticleVersionResponse
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    version_number = 56 # int | Version number of the article
    is_for_display = False # bool | Set this to true, if you are displaying the article to the end-user. If true, the content of snippets or variables appears in the article. Note: If the value is true, ensure that the article content is not passed for update article endpoints. (optional) (default to False)
    append_sas_token = True # bool | Set this to false to exclude appending SAS token for images/files (optional) (default to True)

    try:
        # Gets article by a version number
        api_response = await api_instance.v2_articles_article_id_versions_version_number_get(article_id, version_number, is_for_display=is_for_display, append_sas_token=append_sas_token)
        print("The response of ArticlesApi->v2_articles_article_id_versions_version_number_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_article_id_versions_version_number_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **version_number** | **int**| Version number of the article | 
 **is_for_display** | **bool**| Set this to true, if you are displaying the article to the end-user. If true, the content of snippets or variables appears in the article. Note: If the value is true, ensure that the article content is not passed for update article endpoints. | [optional] [default to False]
 **append_sas_token** | **bool**| Set this to false to exclude appending SAS token for images/files | [optional] [default to True]

### Return type

[**GetArticleVersionResponse**](GetArticleVersionResponse.md)

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

# **v2_articles_bulkcreate_post**
> BulkCreateArticleResponseCustomer v2_articles_bulkcreate_post(create_article_request=create_article_request)

Adds multiple articles

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.bulk_create_article_response_customer import BulkCreateArticleResponseCustomer
from d361api.models.create_article_request import CreateArticleRequest
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
    api_instance = d361api.ArticlesApi(api_client)
    create_article_request = [{"title":"New Article 1","content":"This is my first article Content.","category_id":"5b291e6b-fa40-4ab9-941e-f8fffc23b376","project_version_id":"46f48bc7-760f-4b07-b2d2-fce4aa8ba234","order":0,"user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","content_type":null,"article_type":null},{"title":"New Article 2","content":"This is my second article Content.","category_id":"5b291e6b-fa40-4ab9-941e-f8fffc23b376","project_version_id":"46f48bc7-760f-4b07-b2d2-fce4aa8ba234","order":0,"user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","content_type":null,"article_type":null}] # List[CreateArticleRequest] |  (optional)

    try:
        # Adds multiple articles
        api_response = await api_instance.v2_articles_bulkcreate_post(create_article_request=create_article_request)
        print("The response of ArticlesApi->v2_articles_bulkcreate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_bulkcreate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_article_request** | [**List[CreateArticleRequest]**](CreateArticleRequest.md)|  | [optional] 

### Return type

[**BulkCreateArticleResponseCustomer**](BulkCreateArticleResponseCustomer.md)

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

# **v2_articles_bulkdelete_article_versions_delete**
> BulkDeleteArticleVersionResonse v2_articles_bulkdelete_article_versions_delete(article_id, lang_code, article_version_numbers)

Delete multiple article versions

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.bulk_delete_article_version_resonse import BulkDeleteArticleVersionResonse
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
    api_instance = d361api.ArticlesApi(api_client)
    article_id = 'article_id_example' # str | The ID of the article
    lang_code = 'lang_code_example' # str | Language code of the article
    article_version_numbers = [56] # List[int] | Array of article version numbers

    try:
        # Delete multiple article versions
        api_response = await api_instance.v2_articles_bulkdelete_article_versions_delete(article_id, lang_code, article_version_numbers)
        print("The response of ArticlesApi->v2_articles_bulkdelete_article_versions_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_bulkdelete_article_versions_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_id** | **str**| The ID of the article | 
 **lang_code** | **str**| Language code of the article | 
 **article_version_numbers** | [**List[int]**](int.md)| Array of article version numbers | 

### Return type

[**BulkDeleteArticleVersionResonse**](BulkDeleteArticleVersionResonse.md)

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

# **v2_articles_bulkdelete_delete**
> BulkDeleteArticleResponse v2_articles_bulkdelete_delete(article_ids)

Deletes multiple articles

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.bulk_delete_article_response import BulkDeleteArticleResponse
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
    api_instance = d361api.ArticlesApi(api_client)
    article_ids = ['article_ids_example'] # List[str] | Array of article IDs

    try:
        # Deletes multiple articles
        api_response = await api_instance.v2_articles_bulkdelete_delete(article_ids)
        print("The response of ArticlesApi->v2_articles_bulkdelete_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_bulkdelete_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **article_ids** | [**List[str]**](str.md)| Array of article IDs | 

### Return type

[**BulkDeleteArticleResponse**](BulkDeleteArticleResponse.md)

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

# **v2_articles_bulkpublish_lang_code_post**
> CreateArticleResponse v2_articles_bulkpublish_lang_code_post(lang_code, bulk_publish_article=bulk_publish_article)

Publishes multiple articles

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.bulk_publish_article import BulkPublishArticle
from d361api.models.create_article_response import CreateArticleResponse
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
    api_instance = d361api.ArticlesApi(api_client)
    lang_code = 'en' # str | Language code of the article (default to 'en')
    bulk_publish_article = [{"article_id":"8bcd4bf9-eb93-40d9-a8df-c3b518660ceb","user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","version_number":1,"publish_message":"multiple article published"},{"article_id":"2ce2607f-6cfa-4bc9-9e47-1dc3843198629","user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","version_number":1,"publish_message":"multiple article published"}] # List[BulkPublishArticle] |  (optional)

    try:
        # Publishes multiple articles
        api_response = await api_instance.v2_articles_bulkpublish_lang_code_post(lang_code, bulk_publish_article=bulk_publish_article)
        print("The response of ArticlesApi->v2_articles_bulkpublish_lang_code_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_bulkpublish_lang_code_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lang_code** | **str**| Language code of the article | [default to &#39;en&#39;]
 **bulk_publish_article** | [**List[BulkPublishArticle]**](BulkPublishArticle.md)|  | [optional] 

### Return type

[**CreateArticleResponse**](CreateArticleResponse.md)

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

# **v2_articles_bulkupdate_put**
> BulkUpdateArticleResponse v2_articles_bulkupdate_put(bulk_update_article=bulk_update_article)

Updates multiple articles

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.bulk_update_article import BulkUpdateArticle
from d361api.models.bulk_update_article_response import BulkUpdateArticleResponse
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
    api_instance = d361api.ArticlesApi(api_client)
    bulk_update_article = [{"article_id":"0e9a3cf2-b5ce-46d4-a637-604cb8407b93","lang_code":"en","title":"Updated Title","content":"updating content","html_content":"<p>updating content</p>","category_id":"68212cec-7a9b-4323-9bb8-33865444a508","hidden":false,"version_number":1,"translation_option":"","source":"","order":0}] # List[BulkUpdateArticle] |  (optional)

    try:
        # Updates multiple articles
        api_response = await api_instance.v2_articles_bulkupdate_put(bulk_update_article=bulk_update_article)
        print("The response of ArticlesApi->v2_articles_bulkupdate_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_bulkupdate_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bulk_update_article** | [**List[BulkUpdateArticle]**](BulkUpdateArticle.md)|  | [optional] 

### Return type

[**BulkUpdateArticleResponse**](BulkUpdateArticleResponse.md)

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

# **v2_articles_post**
> CreateArticleResponse v2_articles_post(create_article_request=create_article_request)

Adds an article to an existing category

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.create_article_request import CreateArticleRequest
from d361api.models.create_article_response import CreateArticleResponse
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
    api_instance = d361api.ArticlesApi(api_client)
    create_article_request = {"title":"New Article","content":"This is my new article Content.","category_id":"5b291e6b-fa40-4ab9-941e-f8fffc23b376","project_version_id":"46f48bc7-760f-4b07-b2d2-fce4aa8ba234","order":0,"user_id":"f11efc6f-e968-4e95-82eb-85ad61559de8","content_type":null,"article_type":null} # CreateArticleRequest |  (optional)

    try:
        # Adds an article to an existing category
        api_response = await api_instance.v2_articles_post(create_article_request=create_article_request)
        print("The response of ArticlesApi->v2_articles_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArticlesApi->v2_articles_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_article_request** | [**CreateArticleRequest**](CreateArticleRequest.md)|  | [optional] 

### Return type

[**CreateArticleResponse**](CreateArticleResponse.md)

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

