# ImportDocumentationLogAction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message_type** | [**ImportDocumemtationLogMessageType**](ImportDocumemtationLogMessageType.md) | 0 - Error; 1 - Warning; 2 - Info | [optional] 
**message** | **str** | The content of the message | [optional] 
**cancel_operation** | **bool** |  | [optional] 

## Example

```python
from d361api.d361api.import_documentation_log_action import ImportDocumentationLogAction

# TODO update the JSON string below
json = "{}"
# create an instance of ImportDocumentationLogAction from a JSON string
import_documentation_log_action_instance = ImportDocumentationLogAction.from_json(json)
# print the JSON string representation of the object
print(ImportDocumentationLogAction.to_json())

# convert the object into a dict
import_documentation_log_action_dict = import_documentation_log_action_instance.to_dict()
# create an instance of ImportDocumentationLogAction from a dict
import_documentation_log_action_from_dict = ImportDocumentationLogAction.from_dict(import_documentation_log_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


