# RoleMetaData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the role | [optional] 
**title** | **str** | Name of the role | [optional] 
**description** | **str** | Description of role | [optional] 
**is_system_role** | **bool** | If true, it indicates that the role is one of the system default roles. | [optional] 
**role_type** | [**RoleType**](RoleType.md) | Indicates if the role is a portal role or a content role | [optional] 

## Example

```python
from d361api.d361api.role_meta_data import RoleMetaData

# TODO update the JSON string below
json = "{}"
# create an instance of RoleMetaData from a JSON string
role_meta_data_instance = RoleMetaData.from_json(json)
# print the JSON string representation of the object
print(RoleMetaData.to_json())

# convert the object into a dict
role_meta_data_dict = role_meta_data_instance.to_dict()
# create an instance of RoleMetaData from a dict
role_meta_data_from_dict = RoleMetaData.from_dict(role_meta_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


