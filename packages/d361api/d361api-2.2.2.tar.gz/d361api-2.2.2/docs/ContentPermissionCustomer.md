# ContentPermissionCustomer

The content permission of the team account

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**associated_content_role_id** | **str** | The content role id of the team account.Please refer GET **/Teams/roles** endpoint to get the list of content roles. | 
**access_scope** | [**AddUpdateAccessScopeCustomerV2**](AddUpdateAccessScopeCustomerV2.md) | The access level of the team account. With the access level, you will be able to set the permissions at a granular level. For example, you can limit the user to view articles only for a particular language/category/version. | 

## Example

```python
from d361api.d361api.content_permission_customer import ContentPermissionCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of ContentPermissionCustomer from a JSON string
content_permission_customer_instance = ContentPermissionCustomer.from_json(json)
# print the JSON string representation of the object
print(ContentPermissionCustomer.to_json())

# convert the object into a dict
content_permission_customer_dict = content_permission_customer_instance.to_dict()
# create an instance of ContentPermissionCustomer from a dict
content_permission_customer_from_dict = ContentPermissionCustomer.from_dict(content_permission_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


