# RoleSummaryCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role_id** | **str** |  | [optional] 
**role_name** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.role_summary_customer import RoleSummaryCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of RoleSummaryCustomer from a JSON string
role_summary_customer_instance = RoleSummaryCustomer.from_json(json)
# print the JSON string representation of the object
print(RoleSummaryCustomer.to_json())

# convert the object into a dict
role_summary_customer_dict = role_summary_customer_instance.to_dict()
# create an instance of RoleSummaryCustomer from a dict
role_summary_customer_from_dict = RoleSummaryCustomer.from_dict(role_summary_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


