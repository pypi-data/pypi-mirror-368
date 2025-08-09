# Language


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**code** | **str** |  | [optional] 
**set_as_default** | **bool** |  | [optional] 
**hidden** | **bool** |  | [optional] 
**enable_rtl** | **bool** |  | [optional] 
**site_protection_level** | [**ProjectProtection**](ProjectProtection.md) |  | [optional] 
**is_inheritance_disabled** | **bool** |  | [optional] 
**has_inheritance_disabled_categories_or_articles** | **bool** |  | [optional] 
**country_flag_code** | **str** |  | [optional] 
**display_name** | **str** |  | [optional] 
**is_home_page_enabled** | **bool** |  | [optional] 
**version_display_name** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.language import Language

# TODO update the JSON string below
json = "{}"
# create an instance of Language from a JSON string
language_instance = Language.from_json(json)
# print the JSON string representation of the object
print(Language.to_json())

# convert the object into a dict
language_dict = language_instance.to_dict()
# create an instance of Language from a dict
language_from_dict = Language.from_dict(language_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


