# VectorSearchReferenceArticles


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**citation_id** | **str** |  | [optional] 
**category_id** | **str** |  | [optional] 
**category_title** | **str** |  | [optional] 
**category_slug** | **str** |  | [optional] 
**version_name** | **str** |  | [optional] 
**version_slug** | **str** |  | [optional] 
**article_id** | **str** |  | [optional] 
**article_title** | **str** |  | [optional] 
**article_slug** | **str** |  | [optional] 
**version_display_name** | **str** |  | [optional] 
**language_code** | **str** |  | [optional] 
**data_source_type** | [**DataSourceType**](DataSourceType.md) |  | [optional] 
**external_source_link** | **str** |  | [optional] 
**external_source_name** | **str** |  | [optional] 
**external_source_id** | **str** |  | [optional] 
**is_attachment** | **bool** |  | [optional] 
**attachment_url** | **str** |  | [optional] 
**attachment_title** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.vector_search_reference_articles import VectorSearchReferenceArticles

# TODO update the JSON string below
json = "{}"
# create an instance of VectorSearchReferenceArticles from a JSON string
vector_search_reference_articles_instance = VectorSearchReferenceArticles.from_json(json)
# print the JSON string representation of the object
print(VectorSearchReferenceArticles.to_json())

# convert the object into a dict
vector_search_reference_articles_dict = vector_search_reference_articles_instance.to_dict()
# create an instance of VectorSearchReferenceArticles from a dict
vector_search_reference_articles_from_dict = VectorSearchReferenceArticles.from_dict(vector_search_reference_articles_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


