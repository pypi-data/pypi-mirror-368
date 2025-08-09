# UpdateCategoryContentRequest

Update category content

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category_id** | **str** | Category ID for updating the content | [optional] 
**lang_code** | **str** | Language Code for updating the content | [optional] 
**title** | **str** | The title of the category | [optional] 
**content** | **str** | The content of the category, for any Editor type, use this property. | [optional] 
**html_content** | **str** | The HTML content of the category. If the editor type is WYSIWYG (HTML), use this property - (This property is deprecated and will be removed in a future version of the API, Kindly use **content** property instead of this.) | [optional] 
**block_content** | **str** | The HTML content of the category. If the editor type is Block Editor (HTML), use this property - (This property is deprecated and will be removed in a future version of the API, Kindly use **content** property instead of this.) | [optional] 
**version_number** | **int** | The version number of the category to be updated. The latest version is updated by default. | [optional] 
**translation_option** | **str** | Translation status of the category. 0 - None, 1 - Needs translation, 2 Translated | [optional] 
**source** | **str** | Free text used for future reference | [optional] 
**updated_by** | **str** | The ID of the team account responsible for the category update | [optional] 

## Example

```python
from d361api.d361api.update_category_content_request import UpdateCategoryContentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateCategoryContentRequest from a JSON string
update_category_content_request_instance = UpdateCategoryContentRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateCategoryContentRequest.to_json())

# convert the object into a dict
update_category_content_request_dict = update_category_content_request_instance.to_dict()
# create an instance of UpdateCategoryContentRequest from a dict
update_category_content_request_from_dict = UpdateCategoryContentRequest.from_dict(update_category_content_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


