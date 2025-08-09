# SearchProjectVersionResponseCustomerApi


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**ArticleMatchedData**](ArticleMatchedData.md) |  | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.search_project_version_response_customer_api import SearchProjectVersionResponseCustomerApi

# TODO update the JSON string below
json = "{}"
# create an instance of SearchProjectVersionResponseCustomerApi from a JSON string
search_project_version_response_customer_api_instance = SearchProjectVersionResponseCustomerApi.from_json(json)
# print the JSON string representation of the object
print(SearchProjectVersionResponseCustomerApi.to_json())

# convert the object into a dict
search_project_version_response_customer_api_dict = search_project_version_response_customer_api_instance.to_dict()
# create an instance of SearchProjectVersionResponseCustomerApi from a dict
search_project_version_response_customer_api_from_dict = SearchProjectVersionResponseCustomerApi.from_dict(search_project_version_response_customer_api_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


