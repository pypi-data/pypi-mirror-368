# BaseError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**extension_data** | **object** | This is the Extension data object | [optional] 
**stack_trace** | **str** | A technical trace showing where the error occurred within the system. Intended for backend debugging. | [optional] 
**description** | **str** | A clear message explaining what caused the error. This helps quickly understand what went wrong. | [optional] 
**error_code** | **str** | A short, predefined code that identifies the type of error. Useful for logging the error or raising a support request. | [optional] 
**custom_data** | **Dict[str, object]** | Any structured metadata for the error object. | [optional] 

## Example

```python
from d361api.d361api.base_error import BaseError

# TODO update the JSON string below
json = "{}"
# create an instance of BaseError from a JSON string
base_error_instance = BaseError.from_json(json)
# print the JSON string representation of the object
print(BaseError.to_json())

# convert the object into a dict
base_error_dict = base_error_instance.to_dict()
# create an instance of BaseError from a dict
base_error_from_dict = BaseError.from_dict(base_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


