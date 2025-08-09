# UnpublishCategoryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The ID of the team account who is responsible for the unpublish | 
**project_version_id** | **str** | The project version ID where the article exists. | 
**version_number** | **int** | The version number of the category | 
**unpublish_message** | **str** | Unublish message for the category | [optional] 

## Example

```python
from d361api.d361api.unpublish_category_request import UnpublishCategoryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UnpublishCategoryRequest from a JSON string
unpublish_category_request_instance = UnpublishCategoryRequest.from_json(json)
# print the JSON string representation of the object
print(UnpublishCategoryRequest.to_json())

# convert the object into a dict
unpublish_category_request_dict = unpublish_category_request_instance.to_dict()
# create an instance of UnpublishCategoryRequest from a dict
unpublish_category_request_from_dict = UnpublishCategoryRequest.from_dict(unpublish_category_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


