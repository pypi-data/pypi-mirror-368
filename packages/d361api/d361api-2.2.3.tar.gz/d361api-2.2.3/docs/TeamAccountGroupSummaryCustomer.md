# TeamAccountGroupSummaryCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**group_id** | **str** | The ID of the team account group. | [optional] 
**title** | **str** | The name of the team account group. | [optional] 
**description** | **str** | Description of the team account group. | [optional] 

## Example

```python
from d361api.d361api.team_account_group_summary_customer import TeamAccountGroupSummaryCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of TeamAccountGroupSummaryCustomer from a JSON string
team_account_group_summary_customer_instance = TeamAccountGroupSummaryCustomer.from_json(json)
# print the JSON string representation of the object
print(TeamAccountGroupSummaryCustomer.to_json())

# convert the object into a dict
team_account_group_summary_customer_dict = team_account_group_summary_customer_instance.to_dict()
# create an instance of TeamAccountGroupSummaryCustomer from a dict
team_account_group_summary_customer_from_dict = TeamAccountGroupSummaryCustomer.from_dict(team_account_group_summary_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


