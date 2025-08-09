# BulkUnpublishCategoryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**categories** | [**List[BulkUnpublishCategory]**](BulkUnpublishCategory.md) | Details of the categories need to be unpublished | 
**user_id** | **str** | The ID of the team account that will be marked as the contributor of this unpublish | 
**project_version_id** | **str** | The project version ID where the category exists. | 
**unpublish_message** | **str** | The unpublish message of the category | [optional] 

## Example

```python
from d361api.d361api.bulk_unpublish_category_request import BulkUnpublishCategoryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkUnpublishCategoryRequest from a JSON string
bulk_unpublish_category_request_instance = BulkUnpublishCategoryRequest.from_json(json)
# print the JSON string representation of the object
print(BulkUnpublishCategoryRequest.to_json())

# convert the object into a dict
bulk_unpublish_category_request_dict = bulk_unpublish_category_request_instance.to_dict()
# create an instance of BulkUnpublishCategoryRequest from a dict
bulk_unpublish_category_request_from_dict = BulkUnpublishCategoryRequest.from_dict(bulk_unpublish_category_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


