# d361api.TeamsApi

All URIs are relative to *https://apihub.document360.io*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v2_teams_email_exists_get**](TeamsApi.md#v2_teams_email_exists_get) | **GET** /v2/Teams/email-exists | Checks if email already exists in the project
[**v2_teams_get**](TeamsApi.md#v2_teams_get) | **GET** /v2/Teams | Get all team accounts
[**v2_teams_groups_get**](TeamsApi.md#v2_teams_groups_get) | **GET** /v2/Teams/groups | Get all user groups
[**v2_teams_post**](TeamsApi.md#v2_teams_post) | **POST** /v2/Teams | Adds a new Team Account
[**v2_teams_roles_get**](TeamsApi.md#v2_teams_roles_get) | **GET** /v2/Teams/roles | Get all available roles including default as well as custom roles
[**v2_teams_user_id_content_put**](TeamsApi.md#v2_teams_user_id_content_put) | **PUT** /v2/Teams/{userId}/content | Update the content roles of an individual user
[**v2_teams_user_id_delete**](TeamsApi.md#v2_teams_user_id_delete) | **DELETE** /v2/Teams/{userId} | Deletes a user with an ID
[**v2_teams_user_id_get**](TeamsApi.md#v2_teams_user_id_get) | **GET** /v2/Teams/{userId} | Get complete user details by id
[**v2_teams_user_id_groups_put**](TeamsApi.md#v2_teams_user_id_groups_put) | **PUT** /v2/Teams/{userId}/groups | Modify the groups associated with the user
[**v2_teams_user_id_portal_put**](TeamsApi.md#v2_teams_user_id_portal_put) | **PUT** /v2/Teams/{userId}/portal | Update the portal role of a individual user


# **v2_teams_email_exists_get**
> EmailExistsResponse v2_teams_email_exists_get(email_id, is_an_sso_user=is_an_sso_user)

Checks if email already exists in the project

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.email_exists_response import EmailExistsResponse
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
    api_instance = d361api.TeamsApi(api_client)
    email_id = 'email_id_example' # str | Provide email address that has to be checked against the current team account list
    is_an_sso_user = False # bool | Filter SSO team accounts (optional) (default to False)

    try:
        # Checks if email already exists in the project
        api_response = await api_instance.v2_teams_email_exists_get(email_id, is_an_sso_user=is_an_sso_user)
        print("The response of TeamsApi->v2_teams_email_exists_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamsApi->v2_teams_email_exists_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **email_id** | **str**| Provide email address that has to be checked against the current team account list | 
 **is_an_sso_user** | **bool**| Filter SSO team accounts | [optional] [default to False]

### Return type

[**EmailExistsResponse**](EmailExistsResponse.md)

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

# **v2_teams_get**
> TeamAccountSummaryCustomerListCustomerApiResponse v2_teams_get(skip=skip, take=take)

Get all team accounts

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.team_account_summary_customer_list_customer_api_response import TeamAccountSummaryCustomerListCustomerApiResponse
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
    api_instance = d361api.TeamsApi(api_client)
    skip = 0 # int | Specify the number of records to be bypassed and return the remaining results. The default value is 0. (optional) (default to 0)
    take = 20 # int | Specify the number of records to be retrieved. The default value is 20. (optional) (default to 20)

    try:
        # Get all team accounts
        api_response = await api_instance.v2_teams_get(skip=skip, take=take)
        print("The response of TeamsApi->v2_teams_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamsApi->v2_teams_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **int**| Specify the number of records to be bypassed and return the remaining results. The default value is 0. | [optional] [default to 0]
 **take** | **int**| Specify the number of records to be retrieved. The default value is 20. | [optional] [default to 20]

### Return type

[**TeamAccountSummaryCustomerListCustomerApiResponse**](TeamAccountSummaryCustomerListCustomerApiResponse.md)

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

# **v2_teams_groups_get**
> TeamAccountGroupSummaryCustomerListCustomerApiResponse v2_teams_groups_get()

Get all user groups

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.team_account_group_summary_customer_list_customer_api_response import TeamAccountGroupSummaryCustomerListCustomerApiResponse
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
    api_instance = d361api.TeamsApi(api_client)

    try:
        # Get all user groups
        api_response = await api_instance.v2_teams_groups_get()
        print("The response of TeamsApi->v2_teams_groups_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamsApi->v2_teams_groups_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**TeamAccountGroupSummaryCustomerListCustomerApiResponse**](TeamAccountGroupSummaryCustomerListCustomerApiResponse.md)

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

# **v2_teams_post**
> AddUserDataCustomerApiResponse v2_teams_post(add_team_account_customer=add_team_account_customer)

Adds a new Team Account

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.add_team_account_customer import AddTeamAccountCustomer
from d361api.models.add_user_data_customer_api_response import AddUserDataCustomerApiResponse
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
    api_instance = d361api.TeamsApi(api_client)
    add_team_account_customer = {"email_id":"peterjone@mail.com","first_name":"Peter","last_name":"Jone","invited_by":"844fb5c7e-fcbe-4797-b144-1a7ca2508f43","is_sso_user":false,"scheme_name":null,"skip_sso_invitation_email":true,"associated_portal_role_id":"8db42c7e-fcbe-4797-b144-1a7ca2508453","content_permissions":[{"associated_content_role_id":"33b5c7e-fcbe-4797-b144-1a7ca2508f44","access_scope":{"access_level":0,"categories":null,"project_versions":null,"languages":null}}],"associated_groups":null} # AddTeamAccountCustomer |  (optional)

    try:
        # Adds a new Team Account
        api_response = await api_instance.v2_teams_post(add_team_account_customer=add_team_account_customer)
        print("The response of TeamsApi->v2_teams_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamsApi->v2_teams_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **add_team_account_customer** | [**AddTeamAccountCustomer**](AddTeamAccountCustomer.md)|  | [optional] 

### Return type

[**AddUserDataCustomerApiResponse**](AddUserDataCustomerApiResponse.md)

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

# **v2_teams_roles_get**
> RoleMetaDataListCustomerApiResponse v2_teams_roles_get()

Get all available roles including default as well as custom roles

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.role_meta_data_list_customer_api_response import RoleMetaDataListCustomerApiResponse
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
    api_instance = d361api.TeamsApi(api_client)

    try:
        # Get all available roles including default as well as custom roles
        api_response = await api_instance.v2_teams_roles_get()
        print("The response of TeamsApi->v2_teams_roles_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamsApi->v2_teams_roles_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**RoleMetaDataListCustomerApiResponse**](RoleMetaDataListCustomerApiResponse.md)

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

# **v2_teams_user_id_content_put**
> BooleanCustomerApiResponse v2_teams_user_id_content_put(user_id, edit_content_role_customer=edit_content_role_customer)

Update the content roles of an individual user

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.boolean_customer_api_response import BooleanCustomerApiResponse
from d361api.models.edit_content_role_customer import EditContentRoleCustomer
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
    api_instance = d361api.TeamsApi(api_client)
    user_id = 'user_id_example' # str | The ID of the team account for which the content role has to be updated
    edit_content_role_customer = {"content_permissions":[{"associated_content_role_id":"2e29fa1a-37db-4d15-b06b-0261c60d1898","access_scope":{"access_level":0,"categories":[],"project_versions":[],"languages":[]}}],"is_invitation_id":false} # EditContentRoleCustomer |  (optional)

    try:
        # Update the content roles of an individual user
        api_response = await api_instance.v2_teams_user_id_content_put(user_id, edit_content_role_customer=edit_content_role_customer)
        print("The response of TeamsApi->v2_teams_user_id_content_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamsApi->v2_teams_user_id_content_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| The ID of the team account for which the content role has to be updated | 
 **edit_content_role_customer** | [**EditContentRoleCustomer**](EditContentRoleCustomer.md)|  | [optional] 

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

# **v2_teams_user_id_delete**
> CustomerApiBaseResponse v2_teams_user_id_delete(user_id)

Deletes a user with an ID

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
    api_instance = d361api.TeamsApi(api_client)
    user_id = 'user_id_example' # str | The ID of the team account to be deleted

    try:
        # Deletes a user with an ID
        api_response = await api_instance.v2_teams_user_id_delete(user_id)
        print("The response of TeamsApi->v2_teams_user_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamsApi->v2_teams_user_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| The ID of the team account to be deleted | 

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

# **v2_teams_user_id_get**
> CompleteUserInfoCustomerCustomerApiResponse v2_teams_user_id_get(user_id)

Get complete user details by id

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.complete_user_info_customer_customer_api_response import CompleteUserInfoCustomerCustomerApiResponse
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
    api_instance = d361api.TeamsApi(api_client)
    user_id = 'user_id_example' # str | The ID of the team account

    try:
        # Get complete user details by id
        api_response = await api_instance.v2_teams_user_id_get(user_id)
        print("The response of TeamsApi->v2_teams_user_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamsApi->v2_teams_user_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| The ID of the team account | 

### Return type

[**CompleteUserInfoCustomerCustomerApiResponse**](CompleteUserInfoCustomerCustomerApiResponse.md)

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

# **v2_teams_user_id_groups_put**
> BooleanCustomerApiResponse v2_teams_user_id_groups_put(user_id, edit_user_groups_customer=edit_user_groups_customer)

Modify the groups associated with the user

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.boolean_customer_api_response import BooleanCustomerApiResponse
from d361api.models.edit_user_groups_customer import EditUserGroupsCustomer
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
    api_instance = d361api.TeamsApi(api_client)
    user_id = 'user_id_example' # str | The ID of the team account
    edit_user_groups_customer = {"associated_groups":["2e29fa1a-37db-4d15-b06b-0261c60d1898","y529fa1a-gedb-4d15-b76b-0261c60d87t8"],"is_invitation_id":true} # EditUserGroupsCustomer |  (optional)

    try:
        # Modify the groups associated with the user
        api_response = await api_instance.v2_teams_user_id_groups_put(user_id, edit_user_groups_customer=edit_user_groups_customer)
        print("The response of TeamsApi->v2_teams_user_id_groups_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamsApi->v2_teams_user_id_groups_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| The ID of the team account | 
 **edit_user_groups_customer** | [**EditUserGroupsCustomer**](EditUserGroupsCustomer.md)|  | [optional] 

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

# **v2_teams_user_id_portal_put**
> BooleanCustomerApiResponse v2_teams_user_id_portal_put(user_id, edit_portal_role_customer=edit_portal_role_customer)

Update the portal role of a individual user

### Example

* Api Key Authentication (api_token):

```python
import d361api
from d361api.models.boolean_customer_api_response import BooleanCustomerApiResponse
from d361api.models.edit_portal_role_customer import EditPortalRoleCustomer
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
    api_instance = d361api.TeamsApi(api_client)
    user_id = 'user_id_example' # str | The ID of the team account for which the portal role has to be updated
    edit_portal_role_customer = {"associated_portal_role_id":"2e29fa1a-37db-4d15-b06b-0261c60d1898","is_invitation_id":true} # EditPortalRoleCustomer |  (optional)

    try:
        # Update the portal role of a individual user
        api_response = await api_instance.v2_teams_user_id_portal_put(user_id, edit_portal_role_customer=edit_portal_role_customer)
        print("The response of TeamsApi->v2_teams_user_id_portal_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamsApi->v2_teams_user_id_portal_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| The ID of the team account for which the portal role has to be updated | 
 **edit_portal_role_customer** | [**EditPortalRoleCustomer**](EditPortalRoleCustomer.md)|  | [optional] 

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

