# d361api.ReadersApi

All URIs are relative to *https://apihub.document360.io*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_readers_get**](ReadersApi.md#v2_readers_get) | **GET** /v2/Readers | Get all available readers from the project
[**v2_readers_groups_get**](ReadersApi.md#v2_readers_groups_get) | **GET** /v2/Readers/groups | Get all reader groups
[**v2_readers_groups_group_id_delete**](ReadersApi.md#v2_readers_groups_group_id_delete) | **DELETE** /v2/Readers/groups/{groupId} | Deletes a reader group
[**v2_readers_groups_group_id_get**](ReadersApi.md#v2_readers_groups_group_id_get) | **GET** /v2/Readers/groups/{groupId} | Get a reader group via group id
[**v2_readers_groups_group_id_put**](ReadersApi.md#v2_readers_groups_group_id_put) | **PUT** /v2/Readers/groups/{groupId} | Updates a reader group
[**v2_readers_groups_post**](ReadersApi.md#v2_readers_groups_post) | **POST** /v2/Readers/groups | Add a new reader group
[**v2_readers_jwt_delete**](ReadersApi.md#v2_readers_jwt_delete) | **DELETE** /v2/Readers/JWT | Deletes JWT readers from the project
[**v2_readers_post**](ReadersApi.md#v2_readers_post) | **POST** /v2/Readers | Add a new reader
[**v2_readers_reader_id_delete**](ReadersApi.md#v2_readers_reader_id_delete) | **DELETE** /v2/Readers/{readerId} | Deletes a reader from the project
[**v2_readers_reader_id_put**](ReadersApi.md#v2_readers_reader_id_put) | **PUT** /v2/Readers/{readerId} | Updates a reader


# **v2_readers_get**
> GetReaderResponseCustomer v2_readers_get(off_set=off_set, search_email=search_email)

Get all available readers from the project

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.get_reader_response_customer import GetReaderResponseCustomer
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
    api_instance = d361api.ReadersApi(api_client)
    off_set = 1 # int | Specify the pagination to be retrieved. Each pagination retrieves 5000 readers. The default value is 1. (optional) (default to 1)
    search_email = 'search_email_example' # str |  (optional)

    try:
        # Get all available readers from the project
        api_response = await api_instance.v2_readers_get(off_set=off_set, search_email=search_email)
        print("The response of ReadersApi->v2_readers_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReadersApi->v2_readers_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **off_set** | **int**| Specify the pagination to be retrieved. Each pagination retrieves 5000 readers. The default value is 1. | [optional] [default to 1]
 **search_email** | **str**|  | [optional] 

### Return type

[**GetReaderResponseCustomer**](GetReaderResponseCustomer.md)

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

# **v2_readers_groups_get**
> ReaderGroupCustomerV2ListCustomerApiResponse v2_readers_groups_get(off_set=off_set, exclude_readers=exclude_readers)

Get all reader groups

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.reader_group_customer_v2_list_customer_api_response import ReaderGroupCustomerV2ListCustomerApiResponse
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
    api_instance = d361api.ReadersApi(api_client)
    off_set = 1 # int | Specify the pagination to be retrieved. Each pagination retrieves 5 reader groups. The default value is 1. (optional) (default to 1)
    exclude_readers = False # bool | `True` - Readers will be excluded; `False` - Readers will be included (optional) (default to False)

    try:
        # Get all reader groups
        api_response = await api_instance.v2_readers_groups_get(off_set=off_set, exclude_readers=exclude_readers)
        print("The response of ReadersApi->v2_readers_groups_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReadersApi->v2_readers_groups_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **off_set** | **int**| Specify the pagination to be retrieved. Each pagination retrieves 5 reader groups. The default value is 1. | [optional] [default to 1]
 **exclude_readers** | **bool**| &#x60;True&#x60; - Readers will be excluded; &#x60;False&#x60; - Readers will be included | [optional] [default to False]

### Return type

[**ReaderGroupCustomerV2ListCustomerApiResponse**](ReaderGroupCustomerV2ListCustomerApiResponse.md)

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

# **v2_readers_groups_group_id_delete**
> CustomerApiBaseResponse v2_readers_groups_group_id_delete(group_id)

Deletes a reader group

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
    api_instance = d361api.ReadersApi(api_client)
    group_id = 'group_id_example' # str | The ID of the reader group to be deleted

    try:
        # Deletes a reader group
        api_response = await api_instance.v2_readers_groups_group_id_delete(group_id)
        print("The response of ReadersApi->v2_readers_groups_group_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReadersApi->v2_readers_groups_group_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**| The ID of the reader group to be deleted | 

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

# **v2_readers_groups_group_id_get**
> ReaderGroupCustomerV2CustomerApiResponse v2_readers_groups_group_id_get(group_id, off_set=off_set)

Get a reader group via group id

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.reader_group_customer_v2_customer_api_response import ReaderGroupCustomerV2CustomerApiResponse
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
    api_instance = d361api.ReadersApi(api_client)
    group_id = 'group_id_example' # str | The ID of the reader group
    off_set = 1 # int | Specify the pagination to be retrieved. Each pagination retrieves 5000 readers. The default value is 1. (optional) (default to 1)

    try:
        # Get a reader group via group id
        api_response = await api_instance.v2_readers_groups_group_id_get(group_id, off_set=off_set)
        print("The response of ReadersApi->v2_readers_groups_group_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReadersApi->v2_readers_groups_group_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**| The ID of the reader group | 
 **off_set** | **int**| Specify the pagination to be retrieved. Each pagination retrieves 5000 readers. The default value is 1. | [optional] [default to 1]

### Return type

[**ReaderGroupCustomerV2CustomerApiResponse**](ReaderGroupCustomerV2CustomerApiResponse.md)

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

# **v2_readers_groups_group_id_put**
> BooleanCustomerApiResponse v2_readers_groups_group_id_put(group_id, update_reader_group_request_v2=update_reader_group_request_v2)

Updates a reader group

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.boolean_customer_api_response import BooleanCustomerApiResponse
from d361api.models.update_reader_group_request_v2 import UpdateReaderGroupRequestV2
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
    api_instance = d361api.ReadersApi(api_client)
    group_id = 'group_id_example' # str | The ID of the reader group
    update_reader_group_request_v2 = {"title":"UpdatedReadersGroupName","description":"For better undestanding update and breif this group description here.","associated_readers":null,"access_scope":{"access_level":0,"categories":null,"project_versions":null,"languages":null},"associated_invited_sso_users":null} # UpdateReaderGroupRequestV2 |  (optional)

    try:
        # Updates a reader group
        api_response = await api_instance.v2_readers_groups_group_id_put(group_id, update_reader_group_request_v2=update_reader_group_request_v2)
        print("The response of ReadersApi->v2_readers_groups_group_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReadersApi->v2_readers_groups_group_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**| The ID of the reader group | 
 **update_reader_group_request_v2** | [**UpdateReaderGroupRequestV2**](UpdateReaderGroupRequestV2.md)|  | [optional] 

### Return type

[**BooleanCustomerApiResponse**](BooleanCustomerApiResponse.md)

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

# **v2_readers_groups_post**
> StringCustomerApiResponse v2_readers_groups_post(add_reader_group_request_v2=add_reader_group_request_v2)

Add a new reader group

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.add_reader_group_request_v2 import AddReaderGroupRequestV2
from d361api.models.string_customer_api_response import StringCustomerApiResponse
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
    api_instance = d361api.ReadersApi(api_client)
    add_reader_group_request_v2 = {"title":"ReadersGroupName","description":"For better undestanding make a breif note of readers group description.","associated_readers":[],"access_scope":{"access_level":0,"categories":null,"project_versions":null,"languages":null},"associated_invited_sso_users":null} # AddReaderGroupRequestV2 |  (optional)

    try:
        # Add a new reader group
        api_response = await api_instance.v2_readers_groups_post(add_reader_group_request_v2=add_reader_group_request_v2)
        print("The response of ReadersApi->v2_readers_groups_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReadersApi->v2_readers_groups_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **add_reader_group_request_v2** | [**AddReaderGroupRequestV2**](AddReaderGroupRequestV2.md)|  | [optional] 

### Return type

[**StringCustomerApiResponse**](StringCustomerApiResponse.md)

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

# **v2_readers_jwt_delete**
> CustomerApiBaseResponse v2_readers_jwt_delete(email_ids=email_ids)

Deletes JWT readers from the project

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
    api_instance = d361api.ReadersApi(api_client)
    email_ids = ['email_ids_example'] # List[str] |  (optional)

    try:
        # Deletes JWT readers from the project
        api_response = await api_instance.v2_readers_jwt_delete(email_ids=email_ids)
        print("The response of ReadersApi->v2_readers_jwt_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReadersApi->v2_readers_jwt_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **email_ids** | [**List[str]**](str.md)|  | [optional] 

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

# **v2_readers_post**
> StringCustomerApiResponse v2_readers_post(add_reader_request_v2=add_reader_request_v2)

Add a new reader

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.add_reader_request_v2 import AddReaderRequestV2
from d361api.models.string_customer_api_response import StringCustomerApiResponse
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
    api_instance = d361api.ReadersApi(api_client)
    add_reader_request_v2 = {"first_name":"Peter","last_name":"Jone","email_id":"peterjone@mail.com","associated_reader_groups":null,"access_scope":{"access_level":0,"categories":null,"project_versions":null,"languages":null},"is_sso_user":false,"scheme_name":null,"skip_sso_invitation_email":true,"invited_by":"8dfb5c7e-fcbe-4797-b144-1a7ca2508f50"} # AddReaderRequestV2 |  (optional)

    try:
        # Add a new reader
        api_response = await api_instance.v2_readers_post(add_reader_request_v2=add_reader_request_v2)
        print("The response of ReadersApi->v2_readers_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReadersApi->v2_readers_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **add_reader_request_v2** | [**AddReaderRequestV2**](AddReaderRequestV2.md)|  | [optional] 

### Return type

[**StringCustomerApiResponse**](StringCustomerApiResponse.md)

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

# **v2_readers_reader_id_delete**
> CustomerApiBaseResponse v2_readers_reader_id_delete(reader_id)

Deletes a reader from the project

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
    api_instance = d361api.ReadersApi(api_client)
    reader_id = 'reader_id_example' # str | The ID of the reader to be deleted

    try:
        # Deletes a reader from the project
        api_response = await api_instance.v2_readers_reader_id_delete(reader_id)
        print("The response of ReadersApi->v2_readers_reader_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReadersApi->v2_readers_reader_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **reader_id** | **str**| The ID of the reader to be deleted | 

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

# **v2_readers_reader_id_put**
> BooleanCustomerApiResponse v2_readers_reader_id_put(reader_id, update_reader_request_v2=update_reader_request_v2)

Updates a reader

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.boolean_customer_api_response import BooleanCustomerApiResponse
from d361api.models.update_reader_request_v2 import UpdateReaderRequestV2
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
    api_instance = d361api.ReadersApi(api_client)
    reader_id = 'reader_id_example' # str | 
    update_reader_request_v2 = {"first_name":"Peter","last_name":"Jone","associated_reader_groups":["se3f5c7e-fcbe-4797-b144-1a7ca2508f50","4rfb5c7e-fcbe-4797-b144-1a7ca2508f3f"],"access_scope":{"access_level":0,"categories":null,"project_versions":null,"languages":null},"is_invitation_id":false,"sso_user_type":0} # UpdateReaderRequestV2 |  (optional)

    try:
        # Updates a reader
        api_response = await api_instance.v2_readers_reader_id_put(reader_id, update_reader_request_v2=update_reader_request_v2)
        print("The response of ReadersApi->v2_readers_reader_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReadersApi->v2_readers_reader_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **reader_id** | **str**|  | 
 **update_reader_request_v2** | [**UpdateReaderRequestV2**](UpdateReaderRequestV2.md)|  | [optional] 

### Return type

[**BooleanCustomerApiResponse**](BooleanCustomerApiResponse.md)

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

