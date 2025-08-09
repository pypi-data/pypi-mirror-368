# LanguageSummaryCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_version_id** | **str** | The project version ID to which the user should be given access. | [optional] 
**language_code** | **str** | The language to which the user should be given access. | [optional] 

## Example

```python
from d361api.d361api.language_summary_customer import LanguageSummaryCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of LanguageSummaryCustomer from a JSON string
language_summary_customer_instance = LanguageSummaryCustomer.from_json(json)
# print the JSON string representation of the object
print(LanguageSummaryCustomer.to_json())

# convert the object into a dict
language_summary_customer_dict = language_summary_customer_instance.to_dict()
# create an instance of LanguageSummaryCustomer from a dict
language_summary_customer_from_dict = LanguageSummaryCustomer.from_dict(language_summary_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


