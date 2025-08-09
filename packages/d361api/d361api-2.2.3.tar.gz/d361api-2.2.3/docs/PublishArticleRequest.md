# PublishArticleRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The ID of the team account that will be marked as the contributor of this publish | 
**version_number** | **int** | The version number of the article to be published | 
**publish_message** | **str** | The publish message of the article | [optional] 

## Example

```python
from d361api.d361api.publish_article_request import PublishArticleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PublishArticleRequest from a JSON string
publish_article_request_instance = PublishArticleRequest.from_json(json)
# print the JSON string representation of the object
print(PublishArticleRequest.to_json())

# convert the object into a dict
publish_article_request_dict = publish_article_request_instance.to_dict()
# create an instance of PublishArticleRequest from a dict
publish_article_request_from_dict = PublishArticleRequest.from_dict(publish_article_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


