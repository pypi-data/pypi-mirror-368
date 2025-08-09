# FeatureExplorerStatus


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**feature_usage_score** | **float** |  | [optional] 
**section** | [**SectionTypeEnum**](SectionTypeEnum.md) |  | [optional] 
**feature_id** | **str** |  | [optional] 
**feature_name** | [**FeatureListEnum**](FeatureListEnum.md) |  | [optional] 
**advanced_feature_user_role** | [**FeatureExplorerUserRoleEnum**](FeatureExplorerUserRoleEnum.md) |  | [optional] 
**feature_explorer_user_analytics** | [**FeatureExplorerUserAnalyticsEntity**](FeatureExplorerUserAnalyticsEntity.md) |  | [optional] 

## Example

```python
from d361api.d361api.feature_explorer_status import FeatureExplorerStatus

# TODO update the JSON string below
json = "{}"
# create an instance of FeatureExplorerStatus from a JSON string
feature_explorer_status_instance = FeatureExplorerStatus.from_json(json)
# print the JSON string representation of the object
print(FeatureExplorerStatus.to_json())

# convert the object into a dict
feature_explorer_status_dict = feature_explorer_status_instance.to_dict()
# create an instance of FeatureExplorerStatus from a dict
feature_explorer_status_from_dict = FeatureExplorerStatus.from_dict(feature_explorer_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


