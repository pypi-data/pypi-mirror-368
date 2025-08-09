# CreateArticleRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** | The title of the article | 
**content** | **str** | The content of the article, for any Editor type, use this property | [optional] 
**category_id** | **str** | The ID of the category where the article will be created, CategoryId will be null for custom pages | [optional] 
**project_version_id** | **str** | The project version ID in which the article will be created | 
**order** | **int** | The position of the article in the category tree (By default, it will be placed at the bottom of the category) | [optional] 
**user_id** | **str** | The ID of the team account that will be marked as a contributor of the article | 
**content_type** | [**ArticleContentType**](ArticleContentType.md) | 0 - Markdown; 1 - WYSIWYG(HTML); 2 - Advanced WYSIWYG | [optional] 
**article_type** | [**ArticleType**](ArticleType.md) |  | [optional] 

## Example

```python
from d361api.d361api.create_article_request import CreateArticleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateArticleRequest from a JSON string
create_article_request_instance = CreateArticleRequest.from_json(json)
# print the JSON string representation of the object
print(CreateArticleRequest.to_json())

# convert the object into a dict
create_article_request_dict = create_article_request_instance.to_dict()
# create an instance of CreateArticleRequest from a dict
create_article_request_from_dict = CreateArticleRequest.from_dict(create_article_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


