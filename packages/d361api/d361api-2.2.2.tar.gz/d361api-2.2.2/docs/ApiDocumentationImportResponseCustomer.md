# ApiDocumentationImportResponseCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**ApiDocsImportDataCustomer**](ApiDocsImportDataCustomer.md) | Import response data | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.api_documentation_import_response_customer import ApiDocumentationImportResponseCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of ApiDocumentationImportResponseCustomer from a JSON string
api_documentation_import_response_customer_instance = ApiDocumentationImportResponseCustomer.from_json(json)
# print the JSON string representation of the object
print(ApiDocumentationImportResponseCustomer.to_json())

# convert the object into a dict
api_documentation_import_response_customer_dict = api_documentation_import_response_customer_instance.to_dict()
# create an instance of ApiDocumentationImportResponseCustomer from a dict
api_documentation_import_response_customer_from_dict = ApiDocumentationImportResponseCustomer.from_dict(api_documentation_import_response_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


