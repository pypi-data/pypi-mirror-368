# CategorySummaryCustomerV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category_id** | **str** | The category ID to which the user should be given access. | [optional] 
**project_version_id** | **str** | The project version ID to which the category belongs. | [optional] 
**language_code** | **str** | The language to which the user should be given access. | [optional] 

## Example

```python
from d361api.d361api.category_summary_customer_v2 import CategorySummaryCustomerV2

# TODO update the JSON string below
json = "{}"
# create an instance of CategorySummaryCustomerV2 from a JSON string
category_summary_customer_v2_instance = CategorySummaryCustomerV2.from_json(json)
# print the JSON string representation of the object
print(CategorySummaryCustomerV2.to_json())

# convert the object into a dict
category_summary_customer_v2_dict = category_summary_customer_v2_instance.to_dict()
# create an instance of CategorySummaryCustomerV2 from a dict
category_summary_customer_v2_from_dict = CategorySummaryCustomerV2.from_dict(category_summary_customer_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


