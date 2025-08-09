# CategoryScopeCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_version_id** | **str** | The project version id to which the category belongs. | 
**category_id** | **str** | The category id to which the user should be given access. | 
**language_code** | **str** | The language to which the user should be given access. | 

## Example

```python
from d361api.d361api.category_scope_customer import CategoryScopeCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryScopeCustomer from a JSON string
category_scope_customer_instance = CategoryScopeCustomer.from_json(json)
# print the JSON string representation of the object
print(CategoryScopeCustomer.to_json())

# convert the object into a dict
category_scope_customer_dict = category_scope_customer_instance.to_dict()
# create an instance of CategoryScopeCustomer from a dict
category_scope_customer_from_dict = CategoryScopeCustomer.from_dict(category_scope_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


