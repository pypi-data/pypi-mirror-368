# GuideAccessInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**guide_name** | **str** |  | [optional] 
**category_name** | **str** |  | [optional] 
**category_id** | **str** |  | [optional] 
**language_id** | **str** |  | [optional] 
**language_name** | **str** |  | [optional] 
**language_code** | **str** |  | [optional] 
**version_name** | **str** |  | [optional] 
**version_id** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.guide_access_info import GuideAccessInfo

# TODO update the JSON string below
json = "{}"
# create an instance of GuideAccessInfo from a JSON string
guide_access_info_instance = GuideAccessInfo.from_json(json)
# print the JSON string representation of the object
print(GuideAccessInfo.to_json())

# convert the object into a dict
guide_access_info_dict = guide_access_info_instance.to_dict()
# create an instance of GuideAccessInfo from a dict
guide_access_info_from_dict = GuideAccessInfo.from_dict(guide_access_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


