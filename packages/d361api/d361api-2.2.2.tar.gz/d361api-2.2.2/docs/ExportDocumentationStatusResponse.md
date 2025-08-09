# ExportDocumentationStatusResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Current status of the export and it can be either one of these status &#39;Initiated/InProgress/Completed/Error&#39; | [optional] 
**download_url** | **str** | Exported .zip file URL. The download URL will be available when the export status is completed | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.export_documentation_status_response import ExportDocumentationStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ExportDocumentationStatusResponse from a JSON string
export_documentation_status_response_instance = ExportDocumentationStatusResponse.from_json(json)
# print the JSON string representation of the object
print(ExportDocumentationStatusResponse.to_json())

# convert the object into a dict
export_documentation_status_response_dict = export_documentation_status_response_instance.to_dict()
# create an instance of ExportDocumentationStatusResponse from a dict
export_documentation_status_response_from_dict = ExportDocumentationStatusResponse.from_dict(export_documentation_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


