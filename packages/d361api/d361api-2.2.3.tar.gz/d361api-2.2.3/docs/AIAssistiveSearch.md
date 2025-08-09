# AIAssistiveSearch


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prompt** | **str** |  | [optional] 
**result** | **str** |  | [optional] 
**reference_articles** | [**List[VectorSearchReferenceArticles]**](VectorSearchReferenceArticles.md) |  | [optional] 
**limit_exceeded** | **bool** |  | [optional] 
**analytics_id** | **str** |  | [optional] 
**remaining_credits** | **int** |  | [optional] 
**extension_data** | **object** |  | [optional] 
**context** | [**BaseResponseContext**](BaseResponseContext.md) |  | [optional] 
**success** | **bool** |  | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) |  | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) |  | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) |  | [optional] 
**feature_explorer_status** | [**FeatureExplorerStatus**](FeatureExplorerStatus.md) |  | [optional] 
**custom_page_element** | [**UIElement**](UIElement.md) |  | [optional] 

## Example

```python
from d361api.d361api.ai_assistive_search import AIAssistiveSearch

# TODO update the JSON string below
json = "{}"
# create an instance of AIAssistiveSearch from a JSON string
ai_assistive_search_instance = AIAssistiveSearch.from_json(json)
# print the JSON string representation of the object
print(AIAssistiveSearch.to_json())

# convert the object into a dict
ai_assistive_search_dict = ai_assistive_search_instance.to_dict()
# create an instance of AIAssistiveSearch from a dict
ai_assistive_search_from_dict = AIAssistiveSearch.from_dict(ai_assistive_search_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


