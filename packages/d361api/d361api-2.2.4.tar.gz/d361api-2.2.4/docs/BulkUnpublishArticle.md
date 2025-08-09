# BulkUnpublishArticle


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**article_id** | **str** | The ID of the article | 
**version_number** | **int** | The version number of the article to be unpublished | 

## Example

```python
from d361api.d361api.bulk_unpublish_article import BulkUnpublishArticle

# TODO update the JSON string below
json = "{}"
# create an instance of BulkUnpublishArticle from a JSON string
bulk_unpublish_article_instance = BulkUnpublishArticle.from_json(json)
# print the JSON string representation of the object
print(BulkUnpublishArticle.to_json())

# convert the object into a dict
bulk_unpublish_article_dict = bulk_unpublish_article_instance.to_dict()
# create an instance of BulkUnpublishArticle from a dict
bulk_unpublish_article_from_dict = BulkUnpublishArticle.from_dict(bulk_unpublish_article_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


