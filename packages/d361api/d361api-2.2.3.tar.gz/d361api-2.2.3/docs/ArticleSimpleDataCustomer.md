# ArticleSimpleDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the article | [optional] 
**title** | **str** | The article title | [optional] 
**public_version** | **int** | The article version number(revision) that is currently published | [optional] 
**latest_version** | **int** | The latest version number of this article | [optional] 
**language_code** | **str** | The default language code | [optional] 
**hidden** | **bool** | Indicates if the article is visible on the site | [optional] 
**status** | [**ArticleStatusCustomer**](ArticleStatusCustomer.md) | The status of the article: 0 - Draft, 3 - Published | [optional] 
**order** | **int** | The position of the article inside the parent category | [optional] 
**slug** | **str** | The slug of the article | [optional] 
**content_type** | [**ArticleContentType**](ArticleContentType.md) | The content type of the article: Markdown &#x3D; 0, Wysiwyg &#x3D; 1, Block &#x3D; 2 | [optional] 
**translation_option** | [**LanguageTranslationOption**](LanguageTranslationOption.md) | The Translation status of the article | [optional] 
**is_shared_article** | **bool** | &#x60;True&#x60; indicates that the article is shared | [optional] 
**modified_at** | **datetime** | Article modified date time | [optional] 
**current_workflow_status_id** | **str** | Current Workflow status of the article | [optional] 

## Example

```python
from d361api.d361api.article_simple_data_customer import ArticleSimpleDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of ArticleSimpleDataCustomer from a JSON string
article_simple_data_customer_instance = ArticleSimpleDataCustomer.from_json(json)
# print the JSON string representation of the object
print(ArticleSimpleDataCustomer.to_json())

# convert the object into a dict
article_simple_data_customer_dict = article_simple_data_customer_instance.to_dict()
# create an instance of ArticleSimpleDataCustomer from a dict
article_simple_data_customer_from_dict = ArticleSimpleDataCustomer.from_dict(article_simple_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


