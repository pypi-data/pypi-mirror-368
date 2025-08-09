# CategoryDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the category | [optional] 
**name** | **str** | Name of the category | [optional] 
**description** | **str** | Description of the category | [optional] 
**project_version_id** | **str** | The ID of the project version where this category is located | [optional] 
**order** | **int** | The position the category inside the parent category | [optional] 
**parent_category_id** | **str** | The ID of the parent category ( null if top-level ) | [optional] 
**hidden** | **bool** | Indicates if the category is visible on the site ( If \&quot;false,\&quot; all the child categories and articles will be hidden as well ) | [optional] 
**articles** | [**List[ArticleSimpleDataCustomer]**](ArticleSimpleDataCustomer.md) | The list of articles attached to this category | [optional] 
**child_categories** | [**List[CategoryDataCustomer]**](CategoryDataCustomer.md) | The list of categories attached to this category | [optional] 
**icon** | **str** | Unicode representation of the icon or image URL | [optional] 
**slug** | **str** | The slug of the category | [optional] 
**language_code** | **str** | Language code of the category | [optional] 
**category_type** | [**CategoryType**](CategoryType.md) | 0 - Folder, 1 - Page, 2 - Index | [optional] 
**created_at** | **datetime** | Category created date time | [optional] 
**modified_at** | **datetime** | Category modified date time | [optional] 
**status** | [**ArticleStatusCustomer**](ArticleStatusCustomer.md) | The status of the page type category: 0 - Draft, 3 - Published | [optional] 
**content_type** | [**ArticleContentType**](ArticleContentType.md) | The content type of the page type category: Markdown &#x3D; 0, Wysiwyg &#x3D; 1, Block &#x3D; 2 | [optional] 
**current_workflow_status_id** | **str** | Current Workflow status of the article | [optional] 

## Example

```python
from d361api.d361api.category_data_customer import CategoryDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryDataCustomer from a JSON string
category_data_customer_instance = CategoryDataCustomer.from_json(json)
# print the JSON string representation of the object
print(CategoryDataCustomer.to_json())

# convert the object into a dict
category_data_customer_dict = category_data_customer_instance.to_dict()
# create an instance of CategoryDataCustomer from a dict
category_data_customer_from_dict = CategoryDataCustomer.from_dict(category_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


