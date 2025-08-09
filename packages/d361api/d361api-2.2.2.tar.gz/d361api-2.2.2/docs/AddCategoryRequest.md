# AddCategoryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the category | 
**project_version_id** | **str** | The ID of the project version where category has to be added | 
**order** | **int** | The position inside the parent category | [optional] 
**parent_category_id** | **str** | The ID of the parent category. If empty, it will be added as top level category) | [optional] 
**content** | **str** | The content of the article, for any Editor type, use this property | [optional] 
**category_type** | [**CategoryType**](CategoryType.md) | 0 - Folder, 1 - Page, 2 - Index | [optional] 
**user_id** | **str** | The ID of the team account | [optional] 
**content_type** | [**ArticleContentType**](ArticleContentType.md) | 0 - Markdown; 1 - WYSIWYG(HTML); 2 - Advanced WYSIWYG | [optional] 

## Example

```python
from d361api.d361api.add_category_request import AddCategoryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AddCategoryRequest from a JSON string
add_category_request_instance = AddCategoryRequest.from_json(json)
# print the JSON string representation of the object
print(AddCategoryRequest.to_json())

# convert the object into a dict
add_category_request_dict = add_category_request_instance.to_dict()
# create an instance of AddCategoryRequest from a dict
add_category_request_from_dict = AddCategoryRequest.from_dict(add_category_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


