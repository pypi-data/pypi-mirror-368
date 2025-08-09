# DeleteApiReferenceResponseCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[DeleteApiDefinitionCustomer]**](DeleteApiDefinitionCustomer.md) | Response data of the deletion | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.delete_api_reference_response_customer import DeleteApiReferenceResponseCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteApiReferenceResponseCustomer from a JSON string
delete_api_reference_response_customer_instance = DeleteApiReferenceResponseCustomer.from_json(json)
# print the JSON string representation of the object
print(DeleteApiReferenceResponseCustomer.to_json())

# convert the object into a dict
delete_api_reference_response_customer_dict = delete_api_reference_response_customer_instance.to_dict()
# create an instance of DeleteApiReferenceResponseCustomer from a dict
delete_api_reference_response_customer_from_dict = DeleteApiReferenceResponseCustomer.from_dict(delete_api_reference_response_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


