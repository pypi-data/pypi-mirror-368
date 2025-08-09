# CreateArticleResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**ArticleSimpleDataCustomer**](ArticleSimpleDataCustomer.md) | Create article response data | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.create_article_response import CreateArticleResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateArticleResponse from a JSON string
create_article_response_instance = CreateArticleResponse.from_json(json)
# print the JSON string representation of the object
print(CreateArticleResponse.to_json())

# convert the object into a dict
create_article_response_dict = create_article_response_instance.to_dict()
# create an instance of CreateArticleResponse from a dict
create_article_response_from_dict = CreateArticleResponse.from_dict(create_article_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


