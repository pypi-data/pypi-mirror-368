# ProjectLanguage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**language_id** | **str** | The ID of the language | [optional] 
**language_code** | **str** | The code of the language | [optional] 
**language_name** | **str** | The name of the language | [optional] 
**is_set_as_default** | **bool** | &#x60;True&#x60; - Default language of the version; &#x60;False&#x60; - Non-default language of the version | [optional] 
**country_flag_code** | **str** | The code of the country flag | [optional] 

## Example

```python
from d361api.d361api.project_language import ProjectLanguage

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectLanguage from a JSON string
project_language_instance = ProjectLanguage.from_json(json)
# print the JSON string representation of the object
print(ProjectLanguage.to_json())

# convert the object into a dict
project_language_dict = project_language_instance.to_dict()
# create an instance of ProjectLanguage from a dict
project_language_from_dict = ProjectLanguage.from_dict(project_language_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


