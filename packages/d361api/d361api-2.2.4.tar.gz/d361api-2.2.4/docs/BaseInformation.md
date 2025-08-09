# BaseInformation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**extension_data** | **object** | Extension data for customer Api response information | [optional] 
**description** | **str** | A plain message offering helpful context about the response, such as confirmation of fallback logic or skipped operations. | [optional] 

## Example

```python
from d361api.d361api.base_information import BaseInformation

# TODO update the JSON string below
json = "{}"
# create an instance of BaseInformation from a JSON string
base_information_instance = BaseInformation.from_json(json)
# print the JSON string representation of the object
print(BaseInformation.to_json())

# convert the object into a dict
base_information_dict = base_information_instance.to_dict()
# create an instance of BaseInformation from a dict
base_information_from_dict = BaseInformation.from_dict(base_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


