# PublishCategoryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The ID of the team account who is responsible for the publish | 
**version_number** | **int** | The version number of the category | 
**publish_message** | **str** | Publish message for the category | [optional] 

## Example

```python
from d361api.d361api.publish_category_request import PublishCategoryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PublishCategoryRequest from a JSON string
publish_category_request_instance = PublishCategoryRequest.from_json(json)
# print the JSON string representation of the object
print(PublishCategoryRequest.to_json())

# convert the object into a dict
publish_category_request_dict = publish_category_request_instance.to_dict()
# create an instance of PublishCategoryRequest from a dict
publish_category_request_from_dict = PublishCategoryRequest.from_dict(publish_category_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


