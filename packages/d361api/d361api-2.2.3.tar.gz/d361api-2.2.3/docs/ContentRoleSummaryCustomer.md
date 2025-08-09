# ContentRoleSummaryCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version_access** | [**VersionAccessInfo**](VersionAccessInfo.md) |  | [optional] 
**language_access** | [**LanguageAccessInfo**](LanguageAccessInfo.md) |  | [optional] 
**category_access** | [**CategoryAccessInfo**](CategoryAccessInfo.md) |  | [optional] 
**article_access** | [**ArticleAccessInfo**](ArticleAccessInfo.md) |  | [optional] 
**access_scope_level** | [**AccessScopeLevel**](AccessScopeLevel.md) | This is an enum. Possible values are 0 - None, 1 - Category, 2 - Version, 3 - Project, 4 - Lanaguage | [optional] 
**role_id** | **str** |  | [optional] 
**role_name** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.content_role_summary_customer import ContentRoleSummaryCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of ContentRoleSummaryCustomer from a JSON string
content_role_summary_customer_instance = ContentRoleSummaryCustomer.from_json(json)
# print the JSON string representation of the object
print(ContentRoleSummaryCustomer.to_json())

# convert the object into a dict
content_role_summary_customer_dict = content_role_summary_customer_instance.to_dict()
# create an instance of ContentRoleSummaryCustomer from a dict
content_role_summary_customer_from_dict = ContentRoleSummaryCustomer.from_dict(content_role_summary_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


