# ArticleSimpleVersionCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version_number** | **int** | The version number of the article | [optional] 
**created_by** | **str** | Author name | [optional] 
**created_at** | **datetime** | The date the article version was created | [optional] 
**modified_at** | **datetime** | The last time the article version was modified | [optional] 
**base_version** | **int** | The version number from which this article version is derived | [optional] 
**status** | [**ArticleStatusCustomer**](ArticleStatusCustomer.md) | The status of the article: 0 - Draft, 3 - Published | [optional] 
**profile_url** | **str** | Author profile image | [optional] 

## Example

```python
from d361api.d361api.article_simple_version_customer import ArticleSimpleVersionCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of ArticleSimpleVersionCustomer from a JSON string
article_simple_version_customer_instance = ArticleSimpleVersionCustomer.from_json(json)
# print the JSON string representation of the object
print(ArticleSimpleVersionCustomer.to_json())

# convert the object into a dict
article_simple_version_customer_dict = article_simple_version_customer_instance.to_dict()
# create an instance of ArticleSimpleVersionCustomer from a dict
article_simple_version_customer_from_dict = ArticleSimpleVersionCustomer.from_dict(article_simple_version_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


