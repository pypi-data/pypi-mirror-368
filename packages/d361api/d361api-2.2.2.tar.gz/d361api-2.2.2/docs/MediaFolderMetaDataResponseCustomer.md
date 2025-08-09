# MediaFolderMetaDataResponseCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**MediaFolderMetaDataCustomer**](MediaFolderMetaDataCustomer.md) | Media folder response meta data | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.media_folder_meta_data_response_customer import MediaFolderMetaDataResponseCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of MediaFolderMetaDataResponseCustomer from a JSON string
media_folder_meta_data_response_customer_instance = MediaFolderMetaDataResponseCustomer.from_json(json)
# print the JSON string representation of the object
print(MediaFolderMetaDataResponseCustomer.to_json())

# convert the object into a dict
media_folder_meta_data_response_customer_dict = media_folder_meta_data_response_customer_instance.to_dict()
# create an instance of MediaFolderMetaDataResponseCustomer from a dict
media_folder_meta_data_response_customer_from_dict = MediaFolderMetaDataResponseCustomer.from_dict(media_folder_meta_data_response_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


