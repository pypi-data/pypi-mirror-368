# GetApiReferenceDataResponseCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[ApiDefinitionInforamtionCustomer]**](ApiDefinitionInforamtionCustomer.md) |  | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.get_api_reference_data_response_customer import GetApiReferenceDataResponseCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of GetApiReferenceDataResponseCustomer from a JSON string
get_api_reference_data_response_customer_instance = GetApiReferenceDataResponseCustomer.from_json(json)
# print the JSON string representation of the object
print(GetApiReferenceDataResponseCustomer.to_json())

# convert the object into a dict
get_api_reference_data_response_customer_dict = get_api_reference_data_response_customer_instance.to_dict()
# create an instance of GetApiReferenceDataResponseCustomer from a dict
get_api_reference_data_response_customer_from_dict = GetApiReferenceDataResponseCustomer.from_dict(get_api_reference_data_response_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


