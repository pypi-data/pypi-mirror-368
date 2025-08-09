# ContentRoleInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version_access_info** | [**VersionAccessInfo**](VersionAccessInfo.md) |  | [optional] 
**language_access_info** | [**LanguageAccessInfo**](LanguageAccessInfo.md) |  | [optional] 
**category_access_info** | [**CategoryAccessInfo**](CategoryAccessInfo.md) |  | [optional] 
**article_access_info** | [**ArticleAccessInfo**](ArticleAccessInfo.md) |  | [optional] 
**access_scope_level** | [**AccessScopeLevel**](AccessScopeLevel.md) | This is an enum. Possible values are 0 - None, 1 - Category, 2 - Version, 3 - Project, 4 - Lanaguage | [optional] 
**role_name** | **str** |  | [optional] 
**role_id** | **str** |  | [optional] 
**group_name** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.content_role_info import ContentRoleInfo

# TODO update the JSON string below
json = "{}"
# create an instance of ContentRoleInfo from a JSON string
content_role_info_instance = ContentRoleInfo.from_json(json)
# print the JSON string representation of the object
print(ContentRoleInfo.to_json())

# convert the object into a dict
content_role_info_dict = content_role_info_instance.to_dict()
# create an instance of ContentRoleInfo from a dict
content_role_info_from_dict = ContentRoleInfo.from_dict(content_role_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


