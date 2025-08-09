# BulkPublishCategoryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[BulkCategoryResult]**](BulkCategoryResult.md) |  | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.bulk_publish_category_response import BulkPublishCategoryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BulkPublishCategoryResponse from a JSON string
bulk_publish_category_response_instance = BulkPublishCategoryResponse.from_json(json)
# print the JSON string representation of the object
print(BulkPublishCategoryResponse.to_json())

# convert the object into a dict
bulk_publish_category_response_dict = bulk_publish_category_response_instance.to_dict()
# create an instance of BulkPublishCategoryResponse from a dict
bulk_publish_category_response_from_dict = BulkPublishCategoryResponse.from_dict(bulk_publish_category_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


