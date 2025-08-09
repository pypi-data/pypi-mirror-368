# ImportDocumentationStatusResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**import_documentation_log** | [**ImportAPILog**](ImportAPILog.md) | Details about the import | [optional] 
**status** | **str** | Current status of the import and it can be either one of these statuses &#39;Queued/InProgress/Completed/Error&#39; | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.import_documentation_status_response import ImportDocumentationStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ImportDocumentationStatusResponse from a JSON string
import_documentation_status_response_instance = ImportDocumentationStatusResponse.from_json(json)
# print the JSON string representation of the object
print(ImportDocumentationStatusResponse.to_json())

# convert the object into a dict
import_documentation_status_response_dict = import_documentation_status_response_instance.to_dict()
# create an instance of ImportDocumentationStatusResponse from a dict
import_documentation_status_response_from_dict = ImportDocumentationStatusResponse.from_dict(import_documentation_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


