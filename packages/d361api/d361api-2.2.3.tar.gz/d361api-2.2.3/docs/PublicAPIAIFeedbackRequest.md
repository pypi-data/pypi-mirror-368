# PublicAPIAIFeedbackRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entity_id** | **str** | Analytics ID returned by the ask-eddy response. Required to associate feedback with an ask-eddy query. | [optional] 
**is_liked** | **bool** | Set to &#x60;true&#x60; if the user liked the AI response, and &#x60;false&#x60; if the user disliked the response. | [optional] 
**comments** | **str** | Optional user-provided feedback or suggestions about the AI response. | [optional] 
**notify_me_about_changes** | **bool** | Set to &#x60;true&#x60; if the user wants to be notified when there is a response to their feedback. | [optional] 
**feedback_provider_email** | **str** | Email address of the user submitting the feedback. Required if &#x60;notify_me_about_changes&#x60; is set to &#x60;true&#x60;. | [optional] 
**additional_feedback_info** | [**AIAdditionalFeedbackInfo**](AIAdditionalFeedbackInfo.md) | Additional details about the user’s feedback. Helps categorize user feedback and respond effectively. | [optional] 
**feedback_sub_type** | [**FeedbackSubType**](FeedbackSubType.md) | Set to &#x60;0&#x60; if the user did not receive a response to their query. Set to &#x60;1&#x60; if they received a response but were not satisfied with it. | [optional] 

## Example

```python
from d361api.d361api.public_apiai_feedback_request import PublicAPIAIFeedbackRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PublicAPIAIFeedbackRequest from a JSON string
public_apiai_feedback_request_instance = PublicAPIAIFeedbackRequest.from_json(json)
# print the JSON string representation of the object
print(PublicAPIAIFeedbackRequest.to_json())

# convert the object into a dict
public_apiai_feedback_request_dict = public_apiai_feedback_request_instance.to_dict()
# create an instance of PublicAPIAIFeedbackRequest from a dict
public_apiai_feedback_request_from_dict = PublicAPIAIFeedbackRequest.from_dict(public_apiai_feedback_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


