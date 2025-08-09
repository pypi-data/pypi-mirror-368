# ImportDocumentationRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**source_documentation_url** | **str** | Source documentation zip URL and the file format should be satisfied by Document360 standard. The maximum file size should be less than 1GB | [optional] 
**publish_article** | **bool** | Import article and publish. | [optional] 
**import_by** | **str** | Document360 user-id | [optional] 

## Example

```python
from d361api.d361api.import_documentation_request import ImportDocumentationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ImportDocumentationRequest from a JSON string
import_documentation_request_instance = ImportDocumentationRequest.from_json(json)
# print the JSON string representation of the object
print(ImportDocumentationRequest.to_json())

# convert the object into a dict
import_documentation_request_dict = import_documentation_request_instance.to_dict()
# create an instance of ImportDocumentationRequest from a dict
import_documentation_request_from_dict = ImportDocumentationRequest.from_dict(import_documentation_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


