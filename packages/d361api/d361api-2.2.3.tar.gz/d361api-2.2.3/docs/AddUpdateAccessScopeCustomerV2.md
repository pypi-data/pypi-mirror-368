# AddUpdateAccessScopeCustomerV2

The access scope of the user

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_level** | [**AccessScopeLevel**](AccessScopeLevel.md) | This is an enum. Possible values are  0 - None  1 - Category  2 - Version  3 - Project  4 - Lanaguage | 
**categories** | [**List[CategoryScopeCustomer]**](CategoryScopeCustomer.md) | A list of category scope objects.  This is only required if the access level is set 1 - Category | [optional] 
**project_versions** | **List[str]** | A list of project versions  This is only required if the access level is set to 2 - Version | [optional] 
**languages** | [**List[LanguageScopeCustomer]**](LanguageScopeCustomer.md) | A list of language scope objects  This is only required if the access level is set to 4 - Language | [optional] 

## Example

```python
from d361api.d361api.add_update_access_scope_customer_v2 import AddUpdateAccessScopeCustomerV2

# TODO update the JSON string below
json = "{}"
# create an instance of AddUpdateAccessScopeCustomerV2 from a JSON string
add_update_access_scope_customer_v2_instance = AddUpdateAccessScopeCustomerV2.from_json(json)
# print the JSON string representation of the object
print(AddUpdateAccessScopeCustomerV2.to_json())

# convert the object into a dict
add_update_access_scope_customer_v2_dict = add_update_access_scope_customer_v2_instance.to_dict()
# create an instance of AddUpdateAccessScopeCustomerV2 from a dict
add_update_access_scope_customer_v2_from_dict = AddUpdateAccessScopeCustomerV2.from_dict(add_update_access_scope_customer_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


