# LanguageAccessInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**language_id** | **str** |  | [optional] 
**language_name** | **str** |  | [optional] 
**language_code** | **str** |  | [optional] 
**version_name** | **str** |  | [optional] 
**version_id** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.language_access_info import LanguageAccessInfo

# TODO update the JSON string below
json = "{}"
# create an instance of LanguageAccessInfo from a JSON string
language_access_info_instance = LanguageAccessInfo.from_json(json)
# print the JSON string representation of the object
print(LanguageAccessInfo.to_json())

# convert the object into a dict
language_access_info_dict = language_access_info_instance.to_dict()
# create an instance of LanguageAccessInfo from a dict
language_access_info_from_dict = LanguageAccessInfo.from_dict(language_access_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


