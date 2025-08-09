# UserProfileCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**email_id** | **str** |  | [optional] 
**profile_logo_url** | **str** |  | [optional] 
**user_role** | [**UserAccess**](UserAccess.md) |  | [optional] 
**last_login_at** | **datetime** |  | [optional] 
**unique_user_name** | **str** |  | [optional] 
**sso_user_type** | [**SSOUserTypes**](SSOUserTypes.md) | SSO user type 0 - Normal user, 1 - SSO user, 2 - Invited SSO user | [optional] 
**is_sso_user** | **bool** |  | [optional] 

## Example

```python
from d361api.d361api.user_profile_customer import UserProfileCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of UserProfileCustomer from a JSON string
user_profile_customer_instance = UserProfileCustomer.from_json(json)
# print the JSON string representation of the object
print(UserProfileCustomer.to_json())

# convert the object into a dict
user_profile_customer_dict = user_profile_customer_instance.to_dict()
# create an instance of UserProfileCustomer from a dict
user_profile_customer_from_dict = UserProfileCustomer.from_dict(user_profile_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


