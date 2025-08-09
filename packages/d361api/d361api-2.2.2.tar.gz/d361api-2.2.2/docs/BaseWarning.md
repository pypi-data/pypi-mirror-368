# BaseWarning


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**extension_data** | **object** | Extention Data for customer Api warning | [optional] 
**description** | **str** | Warning description | [optional] 
**warning_code** | **str** | warning code for customer Api base response | [optional] 

## Example

```python
from d361api.d361api.base_warning import BaseWarning

# TODO update the JSON string below
json = "{}"
# create an instance of BaseWarning from a JSON string
base_warning_instance = BaseWarning.from_json(json)
# print the JSON string representation of the object
print(BaseWarning.to_json())

# convert the object into a dict
base_warning_dict = base_warning_instance.to_dict()
# create an instance of BaseWarning from a dict
base_warning_from_dict = BaseWarning.from_dict(base_warning_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


