# BulkUnpublishArticleRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**articles** | [**List[BulkUnpublishArticle]**](BulkUnpublishArticle.md) | Details of the articles need to be unpublished | 
**user_id** | **str** | The ID of the team account that will be marked as the contributor of this unpublish | 
**project_version_id** | **str** | The project version ID where the article exists. | 
**unpublish_message** | **str** | The unpublish message of the article | [optional] 

## Example

```python
from d361api.d361api.bulk_unpublish_article_request import BulkUnpublishArticleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkUnpublishArticleRequest from a JSON string
bulk_unpublish_article_request_instance = BulkUnpublishArticleRequest.from_json(json)
# print the JSON string representation of the object
print(BulkUnpublishArticleRequest.to_json())

# convert the object into a dict
bulk_unpublish_article_request_dict = bulk_unpublish_article_request_instance.to_dict()
# create an instance of BulkUnpublishArticleRequest from a dict
bulk_unpublish_article_request_from_dict = BulkUnpublishArticleRequest.from_dict(bulk_unpublish_article_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


