# CategorySettingsCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**slug** | **str** | The slug of the category | [optional] 
**seo_title** | **str** | SEO title of the category | [optional] 
**description** | **str** | SEO description of the category | [optional] 
**allow_comments** | **bool** | Allow comments for category | [optional] 
**show_table_of_contents** | **bool** | &#x60;True&#x60; - Table of Contents will be enabled   &#x60;False&#x60; - Table of Contents will be disabled | [optional] 
**featured_image_url** | **str** | URL of the featured image | [optional] 
**tags** | **List[str]** | List of Tags associated to the category | [optional] 
**status_indicator** | [**ArticleStatusIndicator**](ArticleStatusIndicator.md) | Category status in the knowledge base. 0 - None; 1 - New; 2 - Updated; 3 - Custom | [optional] 
**status_indicator_expiry_date** | **datetime** | The number of days after which the article status will be removed | [optional] 
**exclude_from_search** | **bool** | **true** - The caetgory will not appear in search results in the knowledge base  **false** - The category will appear in search results in the knowledge base | [optional] 
**exclude_from_ai_search** | **bool** | **true** - The AI search assistant will not fetch information from this page category;   **false** - The AI search assistant will not exclude this page category while fetching information | [optional] 
**related_articles** | [**List[RelatedArticleData]**](RelatedArticleData.md) | The list of related article IDs to show in the knowledge base | [optional] 
**content_type** | [**ArticleContentType**](ArticleContentType.md) | 0 - Markdown content; 1 - HTML content | [optional] 
**is_acknowledgement_enabled** | **bool** |  | [optional] 

## Example

```python
from d361api.d361api.category_settings_customer import CategorySettingsCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of CategorySettingsCustomer from a JSON string
category_settings_customer_instance = CategorySettingsCustomer.from_json(json)
# print the JSON string representation of the object
print(CategorySettingsCustomer.to_json())

# convert the object into a dict
category_settings_customer_dict = category_settings_customer_instance.to_dict()
# create an instance of CategorySettingsCustomer from a dict
category_settings_customer_from_dict = CategorySettingsCustomer.from_dict(category_settings_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


