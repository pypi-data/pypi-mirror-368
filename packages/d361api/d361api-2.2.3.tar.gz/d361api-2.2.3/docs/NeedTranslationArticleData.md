# NeedTranslationArticleData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the article | [optional] 
**category_id** | **str** | The ID of the category | [optional] 

## Example

```python
from d361api.d361api.need_translation_article_data import NeedTranslationArticleData

# TODO update the JSON string below
json = "{}"
# create an instance of NeedTranslationArticleData from a JSON string
need_translation_article_data_instance = NeedTranslationArticleData.from_json(json)
# print the JSON string representation of the object
print(NeedTranslationArticleData.to_json())

# convert the object into a dict
need_translation_article_data_dict = need_translation_article_data_instance.to_dict()
# create an instance of NeedTranslationArticleData from a dict
need_translation_article_data_from_dict = NeedTranslationArticleData.from_dict(need_translation_article_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


