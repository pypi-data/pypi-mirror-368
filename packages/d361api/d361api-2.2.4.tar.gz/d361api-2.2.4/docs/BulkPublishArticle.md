# BulkPublishArticle


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**article_id** | **str** | The ID of the article | 
**user_id** | **str** | The ID of the team account that will be marked as the contributor of this publish | 
**version_number** | **int** | The version number of the article to be published | 
**publish_message** | **str** | The publish message of the article | [optional] 

## Example

```python
from d361api.d361api.bulk_publish_article import BulkPublishArticle

# TODO update the JSON string below
json = "{}"
# create an instance of BulkPublishArticle from a JSON string
bulk_publish_article_instance = BulkPublishArticle.from_json(json)
# print the JSON string representation of the object
print(BulkPublishArticle.to_json())

# convert the object into a dict
bulk_publish_article_dict = bulk_publish_article_instance.to_dict()
# create an instance of BulkPublishArticle from a dict
bulk_publish_article_from_dict = BulkPublishArticle.from_dict(bulk_publish_article_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


