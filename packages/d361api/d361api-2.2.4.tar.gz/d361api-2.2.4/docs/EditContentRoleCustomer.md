# EditContentRoleCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content_permissions** | [**List[ContentPermissionCustomer]**](ContentPermissionCustomer.md) | Content permissions of the team account. Note that a team account can have multiple content permissions. | 
**is_invitation_id** | **bool** | Applicable only for SSO team accounts. If temporary invitation ID is passed as team account ID, then set this to true. | [optional] 

## Example

```python
from d361api.d361api.edit_content_role_customer import EditContentRoleCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of EditContentRoleCustomer from a JSON string
edit_content_role_customer_instance = EditContentRoleCustomer.from_json(json)
# print the JSON string representation of the object
print(EditContentRoleCustomer.to_json())

# convert the object into a dict
edit_content_role_customer_dict = edit_content_role_customer_instance.to_dict()
# create an instance of EditContentRoleCustomer from a dict
edit_content_role_customer_from_dict = EditContentRoleCustomer.from_dict(edit_content_role_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


