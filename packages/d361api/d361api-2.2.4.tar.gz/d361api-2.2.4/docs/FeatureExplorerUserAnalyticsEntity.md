# FeatureExplorerUserAnalyticsEntity


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**project_id** | **str** |  | [optional] 
**user_id** | **str** |  | [optional] 
**trophy_status** | [**TrophyStatus**](TrophyStatus.md) |  | [optional] 
**show_default** | **bool** |  | [optional] 
**show_advanced_section_popup** | **bool** |  | [optional] 
**hide_popup** | **bool** |  | [optional] 
**hide_popup_date** | **datetime** |  | [optional] 
**is_advanced_section_unlocked** | **bool** |  | [optional] 
**usage_score** | **float** |  | [optional] 
**features** | [**List[FeatureAnalytics]**](FeatureAnalytics.md) |  | [optional] 
**is_closed_content_reuse_info** | **bool** |  | [optional] 

## Example

```python
from d361api.d361api.feature_explorer_user_analytics_entity import FeatureExplorerUserAnalyticsEntity

# TODO update the JSON string below
json = "{}"
# create an instance of FeatureExplorerUserAnalyticsEntity from a JSON string
feature_explorer_user_analytics_entity_instance = FeatureExplorerUserAnalyticsEntity.from_json(json)
# print the JSON string representation of the object
print(FeatureExplorerUserAnalyticsEntity.to_json())

# convert the object into a dict
feature_explorer_user_analytics_entity_dict = feature_explorer_user_analytics_entity_instance.to_dict()
# create an instance of FeatureExplorerUserAnalyticsEntity from a dict
feature_explorer_user_analytics_entity_from_dict = FeatureExplorerUserAnalyticsEntity.from_dict(feature_explorer_user_analytics_entity_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


