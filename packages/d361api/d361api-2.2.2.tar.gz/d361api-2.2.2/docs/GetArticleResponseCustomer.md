# GetArticleResponseCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**ArticleVersionDataCustomerResponse**](ArticleVersionDataCustomerResponse.md) | Article data | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.get_article_response_customer import GetArticleResponseCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of GetArticleResponseCustomer from a JSON string
get_article_response_customer_instance = GetArticleResponseCustomer.from_json(json)
# print the JSON string representation of the object
print(GetArticleResponseCustomer.to_json())

# convert the object into a dict
get_article_response_customer_dict = get_article_response_customer_instance.to_dict()
# create an instance of GetArticleResponseCustomer from a dict
get_article_response_customer_from_dict = GetArticleResponseCustomer.from_dict(get_article_response_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


