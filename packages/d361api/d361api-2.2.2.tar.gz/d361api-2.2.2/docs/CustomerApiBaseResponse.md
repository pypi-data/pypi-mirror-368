# CustomerApiBaseResponse


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
from d361api.d361api.customer_api_base_response import CustomerApiBaseResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CustomerApiBaseResponse from a JSON string
customer_api_base_response_instance = CustomerApiBaseResponse.from_json(json)
# print the JSON string representation of the object
print(CustomerApiBaseResponse.to_json())

# convert the object into a dict
customer_api_base_response_dict = customer_api_base_response_instance.to_dict()
# create an instance of CustomerApiBaseResponse from a dict
customer_api_base_response_from_dict = CustomerApiBaseResponse.from_dict(customer_api_base_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


