# ForkArticleVersionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version_number** | **int** | The version number of the article to be forked | 
**user_id** | **str** | The ID of the team account that will be marked as the contributor of this fork | 
**lang_code** | **str** | Language code of the article | 

## Example

```python
from d361api.d361api.fork_article_version_request import ForkArticleVersionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ForkArticleVersionRequest from a JSON string
fork_article_version_request_instance = ForkArticleVersionRequest.from_json(json)
# print the JSON string representation of the object
print(ForkArticleVersionRequest.to_json())

# convert the object into a dict
fork_article_version_request_dict = fork_article_version_request_instance.to_dict()
# create an instance of ForkArticleVersionRequest from a dict
fork_article_version_request_from_dict = ForkArticleVersionRequest.from_dict(fork_article_version_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


