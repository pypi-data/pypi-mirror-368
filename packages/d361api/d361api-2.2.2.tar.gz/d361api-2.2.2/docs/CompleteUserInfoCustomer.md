# CompleteUserInfoCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The ID of the user | [optional] 
**first_name** | **str** | First name of the user | [optional] 
**last_name** | **str** | Last name of the user | [optional] 
**email_id** | **str** | Email address of the user | [optional] 
**profile_logo_url** | **str** | Profile image URL of the user | [optional] 
**last_login_at** | **datetime** | Last login date of the user | [optional] 
**portal_role** | [**RoleSummaryCustomer**](RoleSummaryCustomer.md) | The name of the portal role | [optional] 
**content_roles** | [**List[ContentRoleSummaryCustomer]**](ContentRoleSummaryCustomer.md) | The name of content role | [optional] 
**associated_groups** | [**List[GroupInfo]**](GroupInfo.md) | THe group associated with the team account | [optional] 

## Example

```python
from d361api.d361api.complete_user_info_customer import CompleteUserInfoCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of CompleteUserInfoCustomer from a JSON string
complete_user_info_customer_instance = CompleteUserInfoCustomer.from_json(json)
# print the JSON string representation of the object
print(CompleteUserInfoCustomer.to_json())

# convert the object into a dict
complete_user_info_customer_dict = complete_user_info_customer_instance.to_dict()
# create an instance of CompleteUserInfoCustomer from a dict
complete_user_info_customer_from_dict = CompleteUserInfoCustomer.from_dict(complete_user_info_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


