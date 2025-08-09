# AIAdditionalFeedbackInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**need_more_information** | **bool** | User needs more information than what was provided in the AI response. | [optional] 
**difficult_to_understand** | **bool** | The AI response was difficult for the user to understand. | [optional] 
**irrelevant_content** | **bool** | The AI response was not relevant to the user&#39;s query. | [optional] 
**incorrect_source_reference** | **bool** | The source references in the AI response were incorrect or misleading. | [optional] 
**missing_information** | **bool** | Important information was missing from the AI response. | [optional] 
**dont_like_style** | **bool** | The user did not like the style of the AI response. | [optional] 
**others** | **bool** | The user&#39;s feedback does not fall under the predefined categories. | [optional] 
**comments** | **bool** | Indicates whether the user has provided additional comments. | [optional] 

## Example

```python
from d361api.d361api.ai_additional_feedback_info import AIAdditionalFeedbackInfo

# TODO update the JSON string below
json = "{}"
# create an instance of AIAdditionalFeedbackInfo from a JSON string
ai_additional_feedback_info_instance = AIAdditionalFeedbackInfo.from_json(json)
# print the JSON string representation of the object
print(AIAdditionalFeedbackInfo.to_json())

# convert the object into a dict
ai_additional_feedback_info_dict = ai_additional_feedback_info_instance.to_dict()
# create an instance of AIAdditionalFeedbackInfo from a dict
ai_additional_feedback_info_from_dict = AIAdditionalFeedbackInfo.from_dict(ai_additional_feedback_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


