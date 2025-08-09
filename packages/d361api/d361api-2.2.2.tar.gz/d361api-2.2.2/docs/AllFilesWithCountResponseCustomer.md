# AllFilesWithCountResponseCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**AllFilesWithCountCustomer**](AllFilesWithCountCustomer.md) | Search result meta data | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.all_files_with_count_response_customer import AllFilesWithCountResponseCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of AllFilesWithCountResponseCustomer from a JSON string
all_files_with_count_response_customer_instance = AllFilesWithCountResponseCustomer.from_json(json)
# print the JSON string representation of the object
print(AllFilesWithCountResponseCustomer.to_json())

# convert the object into a dict
all_files_with_count_response_customer_dict = all_files_with_count_response_customer_instance.to_dict()
# create an instance of AllFilesWithCountResponseCustomer from a dict
all_files_with_count_response_customer_from_dict = AllFilesWithCountResponseCustomer.from_dict(all_files_with_count_response_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


