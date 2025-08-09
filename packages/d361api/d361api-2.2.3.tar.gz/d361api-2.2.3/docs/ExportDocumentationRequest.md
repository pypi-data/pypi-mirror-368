# ExportDocumentationRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entity** | **str** |  | [optional] 
**version_id** | **List[str]** |  | [optional] 
**selected_languages** | [**List[LanguageMeta]**](LanguageMeta.md) |  | [optional] 
**selected_categories** | [**List[CategoryMeta]**](CategoryMeta.md) |  | [optional] 
**exclude_media_files** | **bool** |  | [optional] 
**filter_by_article_modified_at** | [**DateRange**](DateRange.md) |  | [optional] 
**export_type** | [**ExportType**](ExportType.md) |  | [optional] 

## Example

```python
from d361api.d361api.export_documentation_request import ExportDocumentationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ExportDocumentationRequest from a JSON string
export_documentation_request_instance = ExportDocumentationRequest.from_json(json)
# print the JSON string representation of the object
print(ExportDocumentationRequest.to_json())

# convert the object into a dict
export_documentation_request_dict = export_documentation_request_instance.to_dict()
# create an instance of ExportDocumentationRequest from a dict
export_documentation_request_from_dict = ExportDocumentationRequest.from_dict(export_documentation_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


