# EditPortalRoleCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**associated_portal_role_id** | **str** | Specify the portal role ID to be assigned for the team account. To get the available roles in the project, use the GET /roles endpoint. | 
**is_invitation_id** | **bool** | Applicable only for SSO users. If temporary invitation ID is passed as team account ID, set this to true. | [optional] 

## Example

```python
from d361api.d361api.edit_portal_role_customer import EditPortalRoleCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of EditPortalRoleCustomer from a JSON string
edit_portal_role_customer_instance = EditPortalRoleCustomer.from_json(json)
# print the JSON string representation of the object
print(EditPortalRoleCustomer.to_json())

# convert the object into a dict
edit_portal_role_customer_dict = edit_portal_role_customer_instance.to_dict()
# create an instance of EditPortalRoleCustomer from a dict
edit_portal_role_customer_from_dict = EditPortalRoleCustomer.from_dict(edit_portal_role_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


