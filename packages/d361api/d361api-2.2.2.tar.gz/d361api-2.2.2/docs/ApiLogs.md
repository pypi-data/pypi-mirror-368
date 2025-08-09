# ApiLogs


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Descriptive message represent the problem occur | [optional] 
**pointer** | **str** | Path where the problem occur | [optional] 

## Example

```python
from d361api.d361api.api_logs import ApiLogs

# TODO update the JSON string below
json = "{}"
# create an instance of ApiLogs from a JSON string
api_logs_instance = ApiLogs.from_json(json)
# print the JSON string representation of the object
print(ApiLogs.to_json())

# convert the object into a dict
api_logs_dict = api_logs_instance.to_dict()
# create an instance of ApiLogs from a dict
api_logs_from_dict = ApiLogs.from_dict(api_logs_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


