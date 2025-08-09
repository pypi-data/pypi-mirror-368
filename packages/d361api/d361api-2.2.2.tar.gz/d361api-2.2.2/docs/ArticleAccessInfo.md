# ArticleAccessInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**article_name** | **str** |  | [optional] 
**category_name** | **str** |  | [optional] 
**category_id** | **str** |  | [optional] 
**language_id** | **str** |  | [optional] 
**language_name** | **str** |  | [optional] 
**language_code** | **str** |  | [optional] 
**version_name** | **str** |  | [optional] 
**version_id** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.article_access_info import ArticleAccessInfo

# TODO update the JSON string below
json = "{}"
# create an instance of ArticleAccessInfo from a JSON string
article_access_info_instance = ArticleAccessInfo.from_json(json)
# print the JSON string representation of the object
print(ArticleAccessInfo.to_json())

# convert the object into a dict
article_access_info_dict = article_access_info_instance.to_dict()
# create an instance of ArticleAccessInfo from a dict
article_access_info_from_dict = ArticleAccessInfo.from_dict(article_access_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


