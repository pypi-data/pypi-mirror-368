# GroupInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**content_role_infos** | [**List[ContentRoleInfo]**](ContentRoleInfo.md) |  | [optional] 

## Example

```python
from d361api.d361api.group_info import GroupInfo

# TODO update the JSON string below
json = "{}"
# create an instance of GroupInfo from a JSON string
group_info_instance = GroupInfo.from_json(json)
# print the JSON string representation of the object
print(GroupInfo.to_json())

# convert the object into a dict
group_info_dict = group_info_instance.to_dict()
# create an instance of GroupInfo from a dict
group_info_from_dict = GroupInfo.from_dict(group_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


