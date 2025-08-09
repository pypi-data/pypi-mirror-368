# ImportAPILog


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**new_versions** | **int** | The number of versions imported | [optional] 
**categories** | **int** | The number of categories imported | [optional] 
**articles** | **int** | The number of articles imported | [optional] 
**languages** | **str** | The number of languages imported | [optional] 
**messages** | [**List[ImportDocumentationLogAction]**](ImportDocumentationLogAction.md) |  | [optional] 

## Example

```python
from d361api.d361api.import_api_log import ImportAPILog

# TODO update the JSON string below
json = "{}"
# create an instance of ImportAPILog from a JSON string
import_api_log_instance = ImportAPILog.from_json(json)
# print the JSON string representation of the object
print(ImportAPILog.to_json())

# convert the object into a dict
import_api_log_dict = import_api_log_instance.to_dict()
# create an instance of ImportAPILog from a dict
import_api_log_from_dict = ImportAPILog.from_dict(import_api_log_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


