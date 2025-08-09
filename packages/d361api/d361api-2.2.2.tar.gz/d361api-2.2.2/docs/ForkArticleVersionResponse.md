# ForkArticleVersionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**ArticleSimpleVersionCustomer**](ArticleSimpleVersionCustomer.md) | forked article data | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.fork_article_version_response import ForkArticleVersionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ForkArticleVersionResponse from a JSON string
fork_article_version_response_instance = ForkArticleVersionResponse.from_json(json)
# print the JSON string representation of the object
print(ForkArticleVersionResponse.to_json())

# convert the object into a dict
fork_article_version_response_dict = fork_article_version_response_instance.to_dict()
# create an instance of ForkArticleVersionResponse from a dict
fork_article_version_response_from_dict = ForkArticleVersionResponse.from_dict(fork_article_version_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


