# UpdateCategoryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the category | [optional] 
**order** | **int** | The position of the category. By default, it will be added at the end of the parent category. | [optional] 
**parent_category_id** | **str** | The ID of the category where the category will be moved. By default, it will be created at the first level. | [optional] 
**hidden** | **bool** | Visibility status of the category. **true** - Category will be hidden; **false** - Category will be shown | [optional] 
**icon** | **str** | The icon of the category. Specify the Unicode icon. Example: 📜 (Windows 10 - Win key + . or Mac ⌃-⌘-Space Bar to open emoji menu) | [optional] 
**language** | **str** | Language code of the category. If language is not specified, the category would be updated in the default language. | [optional] 

## Example

```python
from d361api.d361api.update_category_request import UpdateCategoryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateCategoryRequest from a JSON string
update_category_request_instance = UpdateCategoryRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateCategoryRequest.to_json())

# convert the object into a dict
update_category_request_dict = update_category_request_instance.to_dict()
# create an instance of UpdateCategoryRequest from a dict
update_category_request_from_dict = UpdateCategoryRequest.from_dict(update_category_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


