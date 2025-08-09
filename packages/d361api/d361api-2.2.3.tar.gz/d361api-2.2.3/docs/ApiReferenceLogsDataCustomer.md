# ApiReferenceLogsDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**logs_id** | **str** | The API reference Log ID | [optional] 
**user_name** | **str** | The name of the team account | [optional] 
**user_id** | **str** | The ID of the team account | [optional] 
**title** | **str** | Status of API reference | [optional] 
**modified_at** | **datetime** | Modified date/time | [optional] 
**error_count** | **int** | Total errors count | [optional] 
**alerts_count** | **int** | Total alerts count | [optional] 

## Example

```python
from d361api.d361api.api_reference_logs_data_customer import ApiReferenceLogsDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of ApiReferenceLogsDataCustomer from a JSON string
api_reference_logs_data_customer_instance = ApiReferenceLogsDataCustomer.from_json(json)
# print the JSON string representation of the object
print(ApiReferenceLogsDataCustomer.to_json())

# convert the object into a dict
api_reference_logs_data_customer_dict = api_reference_logs_data_customer_instance.to_dict()
# create an instance of ApiReferenceLogsDataCustomer from a dict
api_reference_logs_data_customer_from_dict = ApiReferenceLogsDataCustomer.from_dict(api_reference_logs_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


