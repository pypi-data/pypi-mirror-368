# ExportDocumentationResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the export request. Use this ID to get export details | [optional] 
**status** | **str** | Current status of the export | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.export_documentation_response import ExportDocumentationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ExportDocumentationResponse from a JSON string
export_documentation_response_instance = ExportDocumentationResponse.from_json(json)
# print the JSON string representation of the object
print(ExportDocumentationResponse.to_json())

# convert the object into a dict
export_documentation_response_dict = export_documentation_response_instance.to_dict()
# create an instance of ExportDocumentationResponse from a dict
export_documentation_response_from_dict = ExportDocumentationResponse.from_dict(export_documentation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


