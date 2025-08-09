# UserDetailsCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**user_description** | **str** |  | [optional] 
**unique_user_name** | **str** |  | [optional] 
**email_id** | **str** |  | [optional] 
**profile_logo_url** | **str** |  | [optional] 
**profile_logo_cdn_url** | **str** |  | [optional] 
**is_enterprise_user** | **bool** |  | [optional] 

## Example

```python
from d361api.d361api.user_details_customer import UserDetailsCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of UserDetailsCustomer from a JSON string
user_details_customer_instance = UserDetailsCustomer.from_json(json)
# print the JSON string representation of the object
print(UserDetailsCustomer.to_json())

# convert the object into a dict
user_details_customer_dict = user_details_customer_instance.to_dict()
# create an instance of UserDetailsCustomer from a dict
user_details_customer_from_dict = UserDetailsCustomer.from_dict(user_details_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


