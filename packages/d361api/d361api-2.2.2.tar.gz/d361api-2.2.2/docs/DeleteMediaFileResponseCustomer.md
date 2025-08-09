# DeleteMediaFileResponseCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**task_id** | **str** |  | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.delete_media_file_response_customer import DeleteMediaFileResponseCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteMediaFileResponseCustomer from a JSON string
delete_media_file_response_customer_instance = DeleteMediaFileResponseCustomer.from_json(json)
# print the JSON string representation of the object
print(DeleteMediaFileResponseCustomer.to_json())

# convert the object into a dict
delete_media_file_response_customer_dict = delete_media_file_response_customer_instance.to_dict()
# create an instance of DeleteMediaFileResponseCustomer from a dict
delete_media_file_response_customer_from_dict = DeleteMediaFileResponseCustomer.from_dict(delete_media_file_response_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


