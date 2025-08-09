# BooleanCustomerApiResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**result** | **bool** | Customer API response data | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.boolean_customer_api_response import BooleanCustomerApiResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BooleanCustomerApiResponse from a JSON string
boolean_customer_api_response_instance = BooleanCustomerApiResponse.from_json(json)
# print the JSON string representation of the object
print(BooleanCustomerApiResponse.to_json())

# convert the object into a dict
boolean_customer_api_response_dict = boolean_customer_api_response_instance.to_dict()
# create an instance of BooleanCustomerApiResponse from a dict
boolean_customer_api_response_from_dict = BooleanCustomerApiResponse.from_dict(boolean_customer_api_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


