# ArticleVersionDataCustomerResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the article | [optional] 
**title** | **str** | The title of the article | [optional] 
**content** | **str** | If the article editor is **Markdown**, then the article content will be present in this property | [optional] 
**html_content** | **str** |  If the article editor is **WYSIWYG (HTML)**, then the content will be present in this property.   **Note**: Markdown editor will also have HTML content (read-only). | [optional] 
**category_id** | **str** | The ID of the article&#39;s parent category | [optional] 
**project_version_id** | **str** | The ID of the project version where the article is located | [optional] 
**version_number** | **int** | The currently fetched version number of the article | [optional] 
**public_version** | **int** | The currently published version number of the article | [optional] 
**latest_version** | **int** | The latest version number of the article | [optional] 
**enable_rtl** | **bool** | &#x60;True&#x60; indicates that **Right to Left** alignment is enabled for the article language | [optional] 
**hidden** | **bool** | &#x60;False&#x60; indicates that the article is visible on the site | [optional] 
**status** | [**ArticleStatusCustomer**](ArticleStatusCustomer.md) | The status of the article: 0 - Draft, 3 - Published | [optional] 
**order** | **int** | The position inside the parent category | [optional] 
**created_by** | **str** | The ID of the team account who created the article | [optional] 
**authors** | [**List[UserDetailsCustomer]**](UserDetailsCustomer.md) | The list of contributors in the article | [optional] 
**created_at** | **datetime** | The date on which the article was created | [optional] 
**modified_at** | **datetime** | The date on which the article was last modified | [optional] 
**slug** | **str** | The slug of the article | [optional] 
**is_fall_back_content** | **bool** | &#x60;True&#x60; indicates that the article content is a fallback of the default language content | [optional] 
**description** | **str** | The description of the article | [optional] 
**category_type** | [**CategoryType**](CategoryType.md) | 0 - Folder, 1 - Page, 2 - Index | [optional] 
**content_type** | [**ArticleContentType**](ArticleContentType.md) | 0 - Markdown; 1 - WYSIWYG(HTML); 2 - Advanced WYSIWYG | [optional] 
**is_shared_article** | **bool** | &#x60;True&#x60; indicates that the article is shared | [optional] 
**translation_option** | [**LanguageTranslationOption**](LanguageTranslationOption.md) | The Translation status of the article | [optional] 
**url** | **str** | Url of the article | [optional] 
**current_workflow_status_id** | **str** | Current Workflow status of the article | [optional] 

## Example

```python
from d361api.d361api.article_version_data_customer_response import ArticleVersionDataCustomerResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ArticleVersionDataCustomerResponse from a JSON string
article_version_data_customer_response_instance = ArticleVersionDataCustomerResponse.from_json(json)
# print the JSON string representation of the object
print(ArticleVersionDataCustomerResponse.to_json())

# convert the object into a dict
article_version_data_customer_response_dict = article_version_data_customer_response_instance.to_dict()
# create an instance of ArticleVersionDataCustomerResponse from a dict
article_version_data_customer_response_from_dict = ArticleVersionDataCustomerResponse.from_dict(article_version_data_customer_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


