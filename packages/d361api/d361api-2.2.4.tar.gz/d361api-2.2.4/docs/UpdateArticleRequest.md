# UpdateArticleRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** | The title of the article | [optional] 
**content** | **str** | The content of the article, for any Editor type, use this property. | [optional] 
**html_content** | **str** | The HTML content of the article. If the editor type is WYSIWYG (HTML), use this property - (This property is deprecated and will be removed in a future version of the API.  Kindly use **content** property instead of this.) | [optional] 
**category_id** | **str** | The ID of the category. If the article has to be moved to another category, enter the desired category ID | [optional] 
**hidden** | **bool** | Visibility status of the article. **true** - Article will be hidden; **false** - Article will be shown | [optional] 
**version_number** | **int** | The version number of the article to be updated. The latest version is updated by default. | [optional] 
**translation_option** | **str** | Translation status of the article. 0 - None, 1 - Needs translation, 2 Translated | [optional] 
**source** | **str** | Free text used for future reference | [optional] 
**order** | **int** | To update the position of the article in the category tree. (Default value is 0, and the order starts from 1 when explicitly set or updated). | [optional] 

## Example

```python
from d361api.d361api.update_article_request import UpdateArticleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateArticleRequest from a JSON string
update_article_request_instance = UpdateArticleRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateArticleRequest.to_json())

# convert the object into a dict
update_article_request_dict = update_article_request_instance.to_dict()
# create an instance of UpdateArticleRequest from a dict
update_article_request_from_dict = UpdateArticleRequest.from_dict(update_article_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


