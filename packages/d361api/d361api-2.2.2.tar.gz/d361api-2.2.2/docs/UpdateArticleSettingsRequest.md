# UpdateArticleSettingsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**slug** | **str** | The slug of the article | [optional] 
**seo_title** | **str** | The SEO title of the article | [optional] 
**description** | **str** | The SEO description of the article | [optional] 
**allow_comments** | **bool** | Enable or disable the commenting on the article. **true** - Commenting will be enabled; **false** - Commenting will be disabled | [optional] 
**show_table_of_contents** | **bool** | Enable or disable the Table of Contents (TOC) for the article in the knowledge base. **true** - TOC will be enabled; **false** - TOC will be disabled | [optional] 
**tags** | **List[str]** | Custom article tags | [optional] 
**status_indicator** | [**ArticleStatusIndicator**](ArticleStatusIndicator.md) | Article status in the knowledge base. 0 - None; 1 - New; 2 - Updated; 3 - Custom | [optional] 
**status_indicator_expiry_date** | **datetime** | The date-time when the public article status is removed | [optional] 
**exclude_from_search** | **bool** | **true** - The article will not appear in search results in the knowledge base; **false** - The article will appear in search results in the knowledge base | [optional] 
**exclude_from_ai_search** | **bool** | **true** - The Eddy-AI assistant will not fetch information from this article; **false** - The Eddy-AI assistant will not exclude this article while fetching information | [optional] 
**related_articles** | **List[str]** | The list of related article IDs to show in the knowledge base | [optional] 
**content_type** | [**ArticleContentType**](ArticleContentType.md) | 0 - Markdown; 1 - WYSIWYG(HTML); 2 - Advanced WYSIWYG | [optional] 
**is_acknowledgement_enabled** | **bool** |  | [optional] 

## Example

```python
from d361api.d361api.update_article_settings_request import UpdateArticleSettingsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateArticleSettingsRequest from a JSON string
update_article_settings_request_instance = UpdateArticleSettingsRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateArticleSettingsRequest.to_json())

# convert the object into a dict
update_article_settings_request_dict = update_article_settings_request_instance.to_dict()
# create an instance of UpdateArticleSettingsRequest from a dict
update_article_settings_request_from_dict = UpdateArticleSettingsRequest.from_dict(update_article_settings_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


