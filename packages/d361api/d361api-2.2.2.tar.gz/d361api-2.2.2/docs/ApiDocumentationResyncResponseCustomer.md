# ApiDocumentationResyncResponseCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**ApiDocsResyncDataCustomer**](ApiDocsResyncDataCustomer.md) | Resync response data | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.api_documentation_resync_response_customer import ApiDocumentationResyncResponseCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of ApiDocumentationResyncResponseCustomer from a JSON string
api_documentation_resync_response_customer_instance = ApiDocumentationResyncResponseCustomer.from_json(json)
# print the JSON string representation of the object
print(ApiDocumentationResyncResponseCustomer.to_json())

# convert the object into a dict
api_documentation_resync_response_customer_dict = api_documentation_resync_response_customer_instance.to_dict()
# create an instance of ApiDocumentationResyncResponseCustomer from a dict
api_documentation_resync_response_customer_from_dict = ApiDocumentationResyncResponseCustomer.from_dict(api_documentation_resync_response_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


