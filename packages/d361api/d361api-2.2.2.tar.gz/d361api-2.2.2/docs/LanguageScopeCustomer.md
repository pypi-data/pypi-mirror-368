# LanguageScopeCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_version_id** | **str** | The project version id to which the user should be given access. | 
**language_code** | **str** | The language to which the user should be given access. | 

## Example

```python
from d361api.d361api.language_scope_customer import LanguageScopeCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of LanguageScopeCustomer from a JSON string
language_scope_customer_instance = LanguageScopeCustomer.from_json(json)
# print the JSON string representation of the object
print(LanguageScopeCustomer.to_json())

# convert the object into a dict
language_scope_customer_dict = language_scope_customer_instance.to_dict()
# create an instance of LanguageScopeCustomer from a dict
language_scope_customer_from_dict = LanguageScopeCustomer.from_dict(language_scope_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


