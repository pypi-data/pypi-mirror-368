# UnpublishArticleRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The ID of the team account that will be marked as the contributor of this unpublish | 
**project_version_id** | **str** | The project version ID where the article exists. | 
**version_number** | **int** | The version number of the article to be unpublished | 
**unpublish_message** | **str** | The unpublish message of the article | [optional] 

## Example

```python
from d361api.d361api.unpublish_article_request import UnpublishArticleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UnpublishArticleRequest from a JSON string
unpublish_article_request_instance = UnpublishArticleRequest.from_json(json)
# print the JSON string representation of the object
print(UnpublishArticleRequest.to_json())

# convert the object into a dict
unpublish_article_request_dict = unpublish_article_request_instance.to_dict()
# create an instance of UnpublishArticleRequest from a dict
unpublish_article_request_from_dict = UnpublishArticleRequest.from_dict(unpublish_article_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


