# BulkDeleteArticleResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[BulkArticleResultCustomer]**](BulkArticleResultCustomer.md) | Bulk delete article response | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.bulk_delete_article_response import BulkDeleteArticleResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BulkDeleteArticleResponse from a JSON string
bulk_delete_article_response_instance = BulkDeleteArticleResponse.from_json(json)
# print the JSON string representation of the object
print(BulkDeleteArticleResponse.to_json())

# convert the object into a dict
bulk_delete_article_response_dict = bulk_delete_article_response_instance.to_dict()
# create an instance of BulkDeleteArticleResponse from a dict
bulk_delete_article_response_from_dict = BulkDeleteArticleResponse.from_dict(bulk_delete_article_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


