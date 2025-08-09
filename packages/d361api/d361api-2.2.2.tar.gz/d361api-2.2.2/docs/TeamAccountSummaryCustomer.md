# TeamAccountSummaryCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The ID of the user | [optional] 
**first_name** | **str** | First name of the user | [optional] 
**last_name** | **str** | Last name of the user | [optional] 
**email_id** | **str** | Email address of the user | [optional] 
**profile_logo_url** | **str** | Profile image URL of the user | [optional] 
**portal_role** | **str** | The name of the portal role | [optional] 
**last_login_at** | **datetime** | Last login date of the user | [optional] 

## Example

```python
from d361api.d361api.team_account_summary_customer import TeamAccountSummaryCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of TeamAccountSummaryCustomer from a JSON string
team_account_summary_customer_instance = TeamAccountSummaryCustomer.from_json(json)
# print the JSON string representation of the object
print(TeamAccountSummaryCustomer.to_json())

# convert the object into a dict
team_account_summary_customer_dict = team_account_summary_customer_instance.to_dict()
# create an instance of TeamAccountSummaryCustomer from a dict
team_account_summary_customer_from_dict = TeamAccountSummaryCustomer.from_dict(team_account_summary_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


