# CategorySimpleVersionCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version_number** | **int** | The currently fetched version number of this category page | [optional] 
**created_by** | **str** | The ID of the user that created the category page | [optional] 
**created_at** | **datetime** | The date the category page was created | [optional] 
**modified_at** | **datetime** | The date the category page was last modified | [optional] 
**base_version** | **int** | The base version of the currently fetched category page | [optional] 
**status** | [**ArticleStatusCustomer**](ArticleStatusCustomer.md) | The status of the article: 0 - Draft, 3 - Published | [optional] 
**profile_url** | **str** | The URL of team account&#39;s profile image | [optional] 

## Example

```python
from d361api.d361api.category_simple_version_customer import CategorySimpleVersionCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of CategorySimpleVersionCustomer from a JSON string
category_simple_version_customer_instance = CategorySimpleVersionCustomer.from_json(json)
# print the JSON string representation of the object
print(CategorySimpleVersionCustomer.to_json())

# convert the object into a dict
category_simple_version_customer_dict = category_simple_version_customer_instance.to_dict()
# create an instance of CategorySimpleVersionCustomer from a dict
category_simple_version_customer_from_dict = CategorySimpleVersionCustomer.from_dict(category_simple_version_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


