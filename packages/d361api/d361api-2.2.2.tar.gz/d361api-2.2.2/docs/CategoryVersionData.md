# CategoryVersionData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the category | [optional] 
**title** | **str** | Category title | [optional] 
**content** | **str** | Category page Markdown content | [optional] 
**html_content** | **str** | Category page WYSIWYG(HTML) content | [optional] 
**block_content** | **str** | Category page Advanced WYSIWYG content | [optional] 
**parent_category_id** | **str** | Parent category ID | [optional] 
**project_document_version_id** | **str** | Project document version ID | [optional] 
**version_number** | **int** | The currently fetched version number of this category page | [optional] 
**public_version** | **int** | The version number that is currently published | [optional] 
**latest_version** | **int** | The latest version number(revision) of this  category page. | [optional] 
**enable_rtl** | **bool** | Indicates if Right to Left alignment is enabled for the category page language | [optional] 
**hidden** | **bool** | Indicates if the category page is visible on the site | [optional] 
**status** | [**ArticleStatusCustomer**](ArticleStatusCustomer.md) | The status of the article: 0 - Draft, 3 - Published | [optional] 
**created_by** | **str** | The ID of the user that created the category page | [optional] 
**authors** | [**List[UserProfileCustomer]**](UserProfileCustomer.md) | The list of authors that contributed to this category page | [optional] 
**created_at** | **datetime** | The date the category page was created | [optional] 
**modified_at** | **datetime** | The date the category page was last modified | [optional] 
**slug** | **str** | The slug of the category page | [optional] 
**is_fall_back_content** | **bool** | Indicates whether the category page content is a fallback of the default language content or not | [optional] 
**stale_status** | [**StaleStatus**](StaleStatus.md) | Fresh - Category page is up-to-date  Stale -  Category page requires review | [optional] 
**content_type** | **str** | 0 - Markdown  1 - WYSIWYG(HTML)  2 - Advanced WYSIWYG | [optional] 
**is_block_editor** | **bool** |  | [optional] [readonly] 

## Example

```python
from d361api.d361api.category_version_data import CategoryVersionData

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryVersionData from a JSON string
category_version_data_instance = CategoryVersionData.from_json(json)
# print the JSON string representation of the object
print(CategoryVersionData.to_json())

# convert the object into a dict
category_version_data_dict = category_version_data_instance.to_dict()
# create an instance of CategoryVersionData from a dict
category_version_data_from_dict = CategoryVersionData.from_dict(category_version_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


