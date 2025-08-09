# FeatureAnalytics


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**section** | [**SectionTypeEnum**](SectionTypeEnum.md) |  | [optional] 
**feature_name** | [**FeatureListEnum**](FeatureListEnum.md) |  | [optional] 
**is_feature_explored** | **bool** |  | [optional] 
**time_stamp** | **datetime** |  | [optional] 

## Example

```python
from d361api.d361api.feature_analytics import FeatureAnalytics

# TODO update the JSON string below
json = "{}"
# create an instance of FeatureAnalytics from a JSON string
feature_analytics_instance = FeatureAnalytics.from_json(json)
# print the JSON string representation of the object
print(FeatureAnalytics.to_json())

# convert the object into a dict
feature_analytics_dict = feature_analytics_instance.to_dict()
# create an instance of FeatureAnalytics from a dict
feature_analytics_from_dict = FeatureAnalytics.from_dict(feature_analytics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


