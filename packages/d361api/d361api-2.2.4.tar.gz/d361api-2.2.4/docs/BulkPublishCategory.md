# BulkPublishCategory


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category_id** | **str** | The ID of the category | 
**user_id** | **str** | The ID of the team account responsible for the publish | 
**version_number** | **int** | Version number of the category page | 
**publish_message** | **str** | Publish message for the category | [optional] 

## Example

```python
from d361api.d361api.bulk_publish_category import BulkPublishCategory

# TODO update the JSON string below
json = "{}"
# create an instance of BulkPublishCategory from a JSON string
bulk_publish_category_instance = BulkPublishCategory.from_json(json)
# print the JSON string representation of the object
print(BulkPublishCategory.to_json())

# convert the object into a dict
bulk_publish_category_dict = bulk_publish_category_instance.to_dict()
# create an instance of BulkPublishCategory from a dict
bulk_publish_category_from_dict = BulkPublishCategory.from_dict(bulk_publish_category_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


