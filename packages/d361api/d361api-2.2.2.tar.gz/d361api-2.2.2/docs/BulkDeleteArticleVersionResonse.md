# BulkDeleteArticleVersionResonse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**article_id** | **str** | IDs of the articles | [optional] 
**data** | **str** | Response article data | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.bulk_delete_article_version_resonse import BulkDeleteArticleVersionResonse

# TODO update the JSON string below
json = "{}"
# create an instance of BulkDeleteArticleVersionResonse from a JSON string
bulk_delete_article_version_resonse_instance = BulkDeleteArticleVersionResonse.from_json(json)
# print the JSON string representation of the object
print(BulkDeleteArticleVersionResonse.to_json())

# convert the object into a dict
bulk_delete_article_version_resonse_dict = bulk_delete_article_version_resonse_instance.to_dict()
# create an instance of BulkDeleteArticleVersionResonse from a dict
bulk_delete_article_version_resonse_from_dict = BulkDeleteArticleVersionResonse.from_dict(bulk_delete_article_version_resonse_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


