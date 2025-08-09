# RelatedArticleData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the article | [optional] 
**title** | **str** | The title of the article | [optional] 
**hidden** | **bool** | &#x60;True&#x60; indicates that the article is hidden | [optional] 
**slug** | **str** | The slug of the article | [optional] 

## Example

```python
from d361api.d361api.related_article_data import RelatedArticleData

# TODO update the JSON string below
json = "{}"
# create an instance of RelatedArticleData from a JSON string
related_article_data_instance = RelatedArticleData.from_json(json)
# print the JSON string representation of the object
print(RelatedArticleData.to_json())

# convert the object into a dict
related_article_data_dict = related_article_data_instance.to_dict()
# create an instance of RelatedArticleData from a dict
related_article_data_from_dict = RelatedArticleData.from_dict(related_article_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


