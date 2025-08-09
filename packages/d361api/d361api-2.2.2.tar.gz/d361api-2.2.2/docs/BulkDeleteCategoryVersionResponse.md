# BulkDeleteCategoryVersionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category_id** | **str** | The ID of the category | [optional] 
**data** | **str** | The list of deleted category versions | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.bulk_delete_category_version_response import BulkDeleteCategoryVersionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BulkDeleteCategoryVersionResponse from a JSON string
bulk_delete_category_version_response_instance = BulkDeleteCategoryVersionResponse.from_json(json)
# print the JSON string representation of the object
print(BulkDeleteCategoryVersionResponse.to_json())

# convert the object into a dict
bulk_delete_category_version_response_dict = bulk_delete_category_version_response_instance.to_dict()
# create an instance of BulkDeleteCategoryVersionResponse from a dict
bulk_delete_category_version_response_from_dict = BulkDeleteCategoryVersionResponse.from_dict(bulk_delete_category_version_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


