# VersionAccessInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version_name** | **str** |  | [optional] 
**version_id** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.version_access_info import VersionAccessInfo

# TODO update the JSON string below
json = "{}"
# create an instance of VersionAccessInfo from a JSON string
version_access_info_instance = VersionAccessInfo.from_json(json)
# print the JSON string representation of the object
print(VersionAccessInfo.to_json())

# convert the object into a dict
version_access_info_dict = version_access_info_instance.to_dict()
# create an instance of VersionAccessInfo from a dict
version_access_info_from_dict = VersionAccessInfo.from_dict(version_access_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


