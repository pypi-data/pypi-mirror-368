# GetLanguageFromProjectVersion


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[ProjectLanguage]**](ProjectLanguage.md) | All Language data in a poject | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.get_language_from_project_version import GetLanguageFromProjectVersion

# TODO update the JSON string below
json = "{}"
# create an instance of GetLanguageFromProjectVersion from a JSON string
get_language_from_project_version_instance = GetLanguageFromProjectVersion.from_json(json)
# print the JSON string representation of the object
print(GetLanguageFromProjectVersion.to_json())

# convert the object into a dict
get_language_from_project_version_dict = get_language_from_project_version_instance.to_dict()
# create an instance of GetLanguageFromProjectVersion from a dict
get_language_from_project_version_from_dict = GetLanguageFromProjectVersion.from_dict(get_language_from_project_version_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


