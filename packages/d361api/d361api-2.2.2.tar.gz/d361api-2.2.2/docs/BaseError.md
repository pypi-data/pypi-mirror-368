# BaseError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**extension_data** | **object** | Thids is the Extention data object | [optional] 
**stack_trace** | **str** | Stack trace for error response message | [optional] 
**description** | **str** | Description for error cause | [optional] 
**error_code** | **str** | Error code for Api response | [optional] 
**custom_data** | **Dict[str, object]** |  | [optional] 

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


