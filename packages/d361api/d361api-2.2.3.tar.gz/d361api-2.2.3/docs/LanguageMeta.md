# LanguageMeta


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**version_id** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.language_meta import LanguageMeta

# TODO update the JSON string below
json = "{}"
# create an instance of LanguageMeta from a JSON string
language_meta_instance = LanguageMeta.from_json(json)
# print the JSON string representation of the object
print(LanguageMeta.to_json())

# convert the object into a dict
language_meta_dict = language_meta_instance.to_dict()
# create an instance of LanguageMeta from a dict
language_meta_from_dict = LanguageMeta.from_dict(language_meta_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


