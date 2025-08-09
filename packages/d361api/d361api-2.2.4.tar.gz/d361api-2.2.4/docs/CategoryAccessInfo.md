# CategoryAccessInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category_name** | **str** |  | [optional] 
**category_id** | **str** |  | [optional] 
**language_id** | **str** |  | [optional] 
**language_name** | **str** |  | [optional] 
**language_code** | **str** |  | [optional] 
**version_name** | **str** |  | [optional] 
**version_id** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.category_access_info import CategoryAccessInfo

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryAccessInfo from a JSON string
category_access_info_instance = CategoryAccessInfo.from_json(json)
# print the JSON string representation of the object
print(CategoryAccessInfo.to_json())

# convert the object into a dict
category_access_info_dict = category_access_info_instance.to_dict()
# create an instance of CategoryAccessInfo from a dict
category_access_info_from_dict = CategoryAccessInfo.from_dict(category_access_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


