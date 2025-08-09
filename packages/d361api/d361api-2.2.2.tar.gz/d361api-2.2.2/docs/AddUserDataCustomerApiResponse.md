# AddUserDataCustomerApiResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**result** | [**AddUserData**](AddUserData.md) | Customer API response data | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.add_user_data_customer_api_response import AddUserDataCustomerApiResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AddUserDataCustomerApiResponse from a JSON string
add_user_data_customer_api_response_instance = AddUserDataCustomerApiResponse.from_json(json)
# print the JSON string representation of the object
print(AddUserDataCustomerApiResponse.to_json())

# convert the object into a dict
add_user_data_customer_api_response_dict = add_user_data_customer_api_response_instance.to_dict()
# create an instance of AddUserDataCustomerApiResponse from a dict
add_user_data_customer_api_response_from_dict = AddUserDataCustomerApiResponse.from_dict(add_user_data_customer_api_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


