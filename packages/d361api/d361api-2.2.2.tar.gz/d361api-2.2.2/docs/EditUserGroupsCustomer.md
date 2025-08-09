# EditUserGroupsCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**associated_groups** | **List[str]** | An array of group IDs in which the team account is associated. | 
**is_invitation_id** | **bool** | Applicable only for SSO team accounts. If temporary invitation ID is passed as team account ID, then set this to true. | [optional] 

## Example

```python
from d361api.d361api.edit_user_groups_customer import EditUserGroupsCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of EditUserGroupsCustomer from a JSON string
edit_user_groups_customer_instance = EditUserGroupsCustomer.from_json(json)
# print the JSON string representation of the object
print(EditUserGroupsCustomer.to_json())

# convert the object into a dict
edit_user_groups_customer_dict = edit_user_groups_customer_instance.to_dict()
# create an instance of EditUserGroupsCustomer from a dict
edit_user_groups_customer_from_dict = EditUserGroupsCustomer.from_dict(edit_user_groups_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


