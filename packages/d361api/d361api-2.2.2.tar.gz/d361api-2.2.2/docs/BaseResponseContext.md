# BaseResponseContext


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**extension_data** | **object** |  | [optional] 
**caller_reference** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.base_response_context import BaseResponseContext

# TODO update the JSON string below
json = "{}"
# create an instance of BaseResponseContext from a JSON string
base_response_context_instance = BaseResponseContext.from_json(json)
# print the JSON string representation of the object
print(BaseResponseContext.to_json())

# convert the object into a dict
base_response_context_dict = base_response_context_instance.to_dict()
# create an instance of BaseResponseContext from a dict
base_response_context_from_dict = BaseResponseContext.from_dict(base_response_context_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


