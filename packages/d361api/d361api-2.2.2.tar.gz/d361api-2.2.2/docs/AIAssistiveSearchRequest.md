# AIAssistiveSearchRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prompt** | **str** |  | [optional] 
**version_id** | **str** |  | [optional] 
**language_code** | **str** |  | [optional] 
**enable_citation** | **bool** |  | [optional] 

## Example

```python
from d361api.d361api.ai_assistive_search_request import AIAssistiveSearchRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AIAssistiveSearchRequest from a JSON string
ai_assistive_search_request_instance = AIAssistiveSearchRequest.from_json(json)
# print the JSON string representation of the object
print(AIAssistiveSearchRequest.to_json())

# convert the object into a dict
ai_assistive_search_request_dict = ai_assistive_search_request_instance.to_dict()
# create an instance of AIAssistiveSearchRequest from a dict
ai_assistive_search_request_from_dict = AIAssistiveSearchRequest.from_dict(ai_assistive_search_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


