# d361api.TranslationsApi

All URIs are relative to *https://apihub.document360.io*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_translations_project_version_id_lang_code_get**](TranslationsApi.md#v2_translations_project_version_id_lang_code_get) | **GET** /v2/Translations/{projectVersionId}/{langCode} | Gets articles by translation status


# **v2_translations_project_version_id_lang_code_get**
> GetArticleNotTranslatedResponse v2_translations_project_version_id_lang_code_get(project_version_id, lang_code, status=status)

Gets articles by translation status

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_article_not_translated_response import GetArticleNotTranslatedResponse
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
    api_instance = d361api.TranslationsApi(api_client)
    project_version_id = 'project_version_id_example' # str | The ID of the version
    lang_code = 'en' # str | Language code of the version (default to 'en')
    status = d361api.LanguageTranslationOption() # LanguageTranslationOption | Article translation status  0 - None, 1 - Needs transation, 2 - Translated, 3 - In progress              Default Value is 0 (Need translation) (optional)

    try:
        # Gets articles by translation status
        api_response = await api_instance.v2_translations_project_version_id_lang_code_get(project_version_id, lang_code, status=status)
        print("The response of TranslationsApi->v2_translations_project_version_id_lang_code_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TranslationsApi->v2_translations_project_version_id_lang_code_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_version_id** | **str**| The ID of the version | 
 **lang_code** | **str**| Language code of the version | [default to &#39;en&#39;]
 **status** | [**LanguageTranslationOption**](.md)| Article translation status  0 - None, 1 - Needs transation, 2 - Translated, 3 - In progress              Default Value is 0 (Need translation) | [optional] 

### Return type

[**GetArticleNotTranslatedResponse**](GetArticleNotTranslatedResponse.md)

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

