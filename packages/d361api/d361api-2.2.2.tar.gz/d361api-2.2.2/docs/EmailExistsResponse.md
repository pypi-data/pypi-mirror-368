# EmailExistsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**EmailExists**](EmailExists.md) | Response that checks if the given email address exists in the project | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.email_exists_response import EmailExistsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of EmailExistsResponse from a JSON string
email_exists_response_instance = EmailExistsResponse.from_json(json)
# print the JSON string representation of the object
print(EmailExistsResponse.to_json())

# convert the object into a dict
email_exists_response_dict = email_exists_response_instance.to_dict()
# create an instance of EmailExistsResponse from a dict
email_exists_response_from_dict = EmailExistsResponse.from_dict(email_exists_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


