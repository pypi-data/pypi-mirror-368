# ArticleSettingCustomerResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**url** | **str** | Url of the article | [optional] 
**slug** | **str** | The slug of the article | [optional] 
**seo_title** | **str** | The SEO title of the article | [optional] 
**description** | **str** | The SEO description of the article | [optional] 
**allow_comments** | **bool** | &#x60;True&#x60; indicates that comments are allowed in the article | [optional] 
**show_table_of_contents** | **bool** | &#x60;True&#x60; indicates that Table of Contents are shown in the article | [optional] 
**featured_image_url** | **str** | URL of the featured image | [optional] 
**tags** | **List[str]** | List of tags associated to the article | [optional] 
**status_indicator** | [**ArticleStatusIndicator**](ArticleStatusIndicator.md) | The status of the article: 0 - None, 1 - New, 2 - Updated, 3 - Custom | [optional] 
**status_indicator_expiry_date** | **datetime** | The number of days after which the article status will be removed | [optional] 
**exclude_from_search** | **bool** | &#x60;True&#x60; indicates that the article will not appear in the Knowledge base search results | [optional] 
**exclude_from_ai_search** | **bool** |  | [optional] 
**related_articles** | [**List[RelatedArticleData]**](RelatedArticleData.md) | List of related articles associated to the article | [optional] 
**is_acknowledgement_enabled** | **bool** |  | [optional] 

## Example

```python
from d361api.d361api.article_setting_customer_response import ArticleSettingCustomerResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ArticleSettingCustomerResponse from a JSON string
article_setting_customer_response_instance = ArticleSettingCustomerResponse.from_json(json)
# print the JSON string representation of the object
print(ArticleSettingCustomerResponse.to_json())

# convert the object into a dict
article_setting_customer_response_dict = article_setting_customer_response_instance.to_dict()
# create an instance of ArticleSettingCustomerResponse from a dict
article_setting_customer_response_from_dict = ArticleSettingCustomerResponse.from_dict(article_setting_customer_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


