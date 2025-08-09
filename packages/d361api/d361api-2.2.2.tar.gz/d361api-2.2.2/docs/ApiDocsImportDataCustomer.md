# ApiDocsImportDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**categories_created** | **int** | Total category created | [optional] 
**articles_created** | **int** | Total article created | [optional] 
**api_reference_id** | **str** | Api reference ID | [optional] 
**errors** | [**List[ApiErrorAndWarningsData]**](ApiErrorAndWarningsData.md) | Error log response | [optional] 
**alerts** | [**List[ApiErrorAndWarningsData]**](ApiErrorAndWarningsData.md) | Alerts log response | [optional] 

## Example

```python
from d361api.d361api.api_docs_import_data_customer import ApiDocsImportDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of ApiDocsImportDataCustomer from a JSON string
api_docs_import_data_customer_instance = ApiDocsImportDataCustomer.from_json(json)
# print the JSON string representation of the object
print(ApiDocsImportDataCustomer.to_json())

# convert the object into a dict
api_docs_import_data_customer_dict = api_docs_import_data_customer_instance.to_dict()
# create an instance of ApiDocsImportDataCustomer from a dict
api_docs_import_data_customer_from_dict = ApiDocsImportDataCustomer.from_dict(api_docs_import_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


