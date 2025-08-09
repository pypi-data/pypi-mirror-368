# ApiDocsResyncDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**errors** | [**List[ApiErrorAndWarningsData]**](ApiErrorAndWarningsData.md) | Error log response | [optional] 
**alerts** | [**List[ApiErrorAndWarningsData]**](ApiErrorAndWarningsData.md) | Alerts log response | [optional] 
**categories_created** | **int** | Total categories created | [optional] 
**articles_created** | **int** | Total articles created | [optional] 

## Example

```python
from d361api.d361api.api_docs_resync_data_customer import ApiDocsResyncDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of ApiDocsResyncDataCustomer from a JSON string
api_docs_resync_data_customer_instance = ApiDocsResyncDataCustomer.from_json(json)
# print the JSON string representation of the object
print(ApiDocsResyncDataCustomer.to_json())

# convert the object into a dict
api_docs_resync_data_customer_dict = api_docs_resync_data_customer_instance.to_dict()
# create an instance of ApiDocsResyncDataCustomer from a dict
api_docs_resync_data_customer_from_dict = ApiDocsResyncDataCustomer.from_dict(api_docs_resync_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


