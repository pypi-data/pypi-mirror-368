# CategoryVersionDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the category | [optional] 
**title** | **str** | The title of the category | [optional] 
**content** | **str** | The content of the category | [optional] 
**html_content** | **str** | The HTML content of the category | [optional] 
**block_content** | **str** | The HTML content of the category (Block editor) | [optional] 
**category_id** | **str** | Existing category ID | [optional] 
**project_version_id** | **str** | Existing project version ID | [optional] 
**version_number** | **int** | Category Version Number | [optional] 
**public_version** | **int** | The ID of the project version where this category is located | [optional] 
**latest_version** | **int** | The latest version number of this category | [optional] 
**enable_rtl** | **bool** | Indicates if Right to Left alignment is enabled for the category language | [optional] 
**hidden** | **bool** | Indicates if the category is visible on the site | [optional] 
**status** | [**ArticleStatusCustomer**](ArticleStatusCustomer.md) | The status of the category: 0 - Draft,  3 - Published | [optional] 
**order** | **int** | The position inside the parent category | [optional] 
**created_by** | **str** | The ID of the user that created the category | [optional] 
**authors** | [**List[UserProfileCustomer]**](UserProfileCustomer.md) | The list of authors that contributed to this category | [optional] 
**created_at** | **datetime** | The date the category was created | [optional] 
**modified_at** | **datetime** | The date the category was last modified | [optional] 
**slug** | **str** | The slug of the category | [optional] 
**is_fall_back_content** | **bool** | Indicates whether the category content is a fallback of the default language content or not | [optional] 

## Example

```python
from d361api.d361api.category_version_data_customer import CategoryVersionDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryVersionDataCustomer from a JSON string
category_version_data_customer_instance = CategoryVersionDataCustomer.from_json(json)
# print the JSON string representation of the object
print(CategoryVersionDataCustomer.to_json())

# convert the object into a dict
category_version_data_customer_dict = category_version_data_customer_instance.to_dict()
# create an instance of CategoryVersionDataCustomer from a dict
category_version_data_customer_from_dict = CategoryVersionDataCustomer.from_dict(category_version_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


