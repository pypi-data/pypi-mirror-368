# AccessScopeCustomerV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_level** | [**AccessScopeLevel**](AccessScopeLevel.md) | The access level of the reader group. 0-None, 1-Category, 2-Version, 3-Project, 4-Language | [optional] 
**categories** | [**List[CategorySummaryCustomerV2]**](CategorySummaryCustomerV2.md) | List of category scope objects. | [optional] 
**project_versions** | **List[str]** | List of project version IDs the reader has access to. | [optional] 
**languages** | [**List[LanguageSummaryCustomer]**](LanguageSummaryCustomer.md) | List of language scope objects. | [optional] 

## Example

```python
from d361api.d361api.access_scope_customer_v2 import AccessScopeCustomerV2

# TODO update the JSON string below
json = "{}"
# create an instance of AccessScopeCustomerV2 from a JSON string
access_scope_customer_v2_instance = AccessScopeCustomerV2.from_json(json)
# print the JSON string representation of the object
print(AccessScopeCustomerV2.to_json())

# convert the object into a dict
access_scope_customer_v2_dict = access_scope_customer_v2_instance.to_dict()
# create an instance of AccessScopeCustomerV2 from a dict
access_scope_customer_v2_from_dict = AccessScopeCustomerV2.from_dict(access_scope_customer_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


