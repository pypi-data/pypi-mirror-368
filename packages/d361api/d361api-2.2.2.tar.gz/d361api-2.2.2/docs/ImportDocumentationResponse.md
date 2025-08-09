# ImportDocumentationResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the import request. Use this ID to get the import details | [optional] 
**status** | **str** | Current status of the import | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.import_documentation_response import ImportDocumentationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ImportDocumentationResponse from a JSON string
import_documentation_response_instance = ImportDocumentationResponse.from_json(json)
# print the JSON string representation of the object
print(ImportDocumentationResponse.to_json())

# convert the object into a dict
import_documentation_response_dict = import_documentation_response_instance.to_dict()
# create an instance of ImportDocumentationResponse from a dict
import_documentation_response_from_dict = ImportDocumentationResponse.from_dict(import_documentation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


