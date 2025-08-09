# ApiErrorAndWarningsData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Descriptive message of the problem | [optional] 
**pointer** | **str** | Path where the problem occures | [optional] 

## Example

```python
from d361api.d361api.api_error_and_warnings_data import ApiErrorAndWarningsData

# TODO update the JSON string below
json = "{}"
# create an instance of ApiErrorAndWarningsData from a JSON string
api_error_and_warnings_data_instance = ApiErrorAndWarningsData.from_json(json)
# print the JSON string representation of the object
print(ApiErrorAndWarningsData.to_json())

# convert the object into a dict
api_error_and_warnings_data_dict = api_error_and_warnings_data_instance.to_dict()
# create an instance of ApiErrorAndWarningsData from a dict
api_error_and_warnings_data_from_dict = ApiErrorAndWarningsData.from_dict(api_error_and_warnings_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


