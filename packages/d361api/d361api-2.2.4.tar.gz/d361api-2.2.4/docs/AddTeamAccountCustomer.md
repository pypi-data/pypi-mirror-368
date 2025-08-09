# AddTeamAccountCustomer

Request to add a new team account user

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email_id** | **str** | The email address of the team account | 
**first_name** | **str** | First name of the team account | [optional] 
**last_name** | **str** | Last name of the team account | [optional] 
**invited_by** | **str** | The ID of an existing team account. To get the id, please refer GET **/v2/Teams** endpoint | 
**is_sso_user** | **bool** | Set this to true, if you are adding an SSO user | [optional] 
**scheme_name** | **str** | Specify to add the reader to the specific scheme name, if the reader is a Single Sign-On user. If the scheme name is not provided, then the reader will be added to the default scheme. | [optional] 
**skip_sso_invitation_email** | **bool** | Set this to true, if you would like to avoid sending an invitation email to the newly added team account.  This property is applicable only when adding a SSO user. | [optional] 
**associated_portal_role_id** | **str** | The associated portal role id. To get the list of portal roles refer /teams/roles endpoint. | 
**content_permissions** | [**List[ContentPermissionCustomer]**](ContentPermissionCustomer.md) | The content level permissions for the newly added team account | 
**associated_groups** | **List[str]** | A list of group ids to which the team account has to be added. Please refer /teams/groups endpoint to get the available groups. | [optional] 

## Example

```python
from d361api.d361api.add_team_account_customer import AddTeamAccountCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of AddTeamAccountCustomer from a JSON string
add_team_account_customer_instance = AddTeamAccountCustomer.from_json(json)
# print the JSON string representation of the object
print(AddTeamAccountCustomer.to_json())

# convert the object into a dict
add_team_account_customer_dict = add_team_account_customer_instance.to_dict()
# create an instance of AddTeamAccountCustomer from a dict
add_team_account_customer_from_dict = AddTeamAccountCustomer.from_dict(add_team_account_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


