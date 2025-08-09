# BulkCategoryResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category_id** | **str** | The ID of the category | [optional] 
**success** | **bool** | &#x60;True&#x60; - Category is published  &#x60;False&#x60; - Category is not published | [optional] 
**details** | **str** | Description of the action performed | [optional] 

## Example

```python
from d361api.d361api.bulk_category_result import BulkCategoryResult

# TODO update the JSON string below
json = "{}"
# create an instance of BulkCategoryResult from a JSON string
bulk_category_result_instance = BulkCategoryResult.from_json(json)
# print the JSON string representation of the object
print(BulkCategoryResult.to_json())

# convert the object into a dict
bulk_category_result_dict = bulk_category_result_instance.to_dict()
# create an instance of BulkCategoryResult from a dict
bulk_category_result_from_dict = BulkCategoryResult.from_dict(bulk_category_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


