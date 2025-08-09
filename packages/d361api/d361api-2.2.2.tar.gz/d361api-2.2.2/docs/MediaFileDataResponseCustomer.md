# MediaFileDataResponseCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.media_file_data_response_customer import MediaFileDataResponseCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of MediaFileDataResponseCustomer from a JSON string
media_file_data_response_customer_instance = MediaFileDataResponseCustomer.from_json(json)
# print the JSON string representation of the object
print(MediaFileDataResponseCustomer.to_json())

# convert the object into a dict
media_file_data_response_customer_dict = media_file_data_response_customer_instance.to_dict()
# create an instance of MediaFileDataResponseCustomer from a dict
media_file_data_response_customer_from_dict = MediaFileDataResponseCustomer.from_dict(media_file_data_response_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


