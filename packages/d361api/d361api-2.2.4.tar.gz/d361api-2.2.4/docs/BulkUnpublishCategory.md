# BulkUnpublishCategory


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category_id** | **str** | The ID of the category | 
**version_number** | **int** | The version number of the category to be unpublished | 

## Example

```python
from d361api.d361api.bulk_unpublish_category import BulkUnpublishCategory

# TODO update the JSON string below
json = "{}"
# create an instance of BulkUnpublishCategory from a JSON string
bulk_unpublish_category_instance = BulkUnpublishCategory.from_json(json)
# print the JSON string representation of the object
print(BulkUnpublishCategory.to_json())

# convert the object into a dict
bulk_unpublish_category_dict = bulk_unpublish_category_instance.to_dict()
# create an instance of BulkUnpublishCategory from a dict
bulk_unpublish_category_from_dict = BulkUnpublishCategory.from_dict(bulk_unpublish_category_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


