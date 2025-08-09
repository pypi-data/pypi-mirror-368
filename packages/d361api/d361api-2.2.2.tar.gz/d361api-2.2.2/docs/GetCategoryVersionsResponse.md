# GetCategoryVersionsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**versions** | [**List[CategorySimpleVersionCustomer]**](CategorySimpleVersionCustomer.md) | get category data by version | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.get_category_versions_response import GetCategoryVersionsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetCategoryVersionsResponse from a JSON string
get_category_versions_response_instance = GetCategoryVersionsResponse.from_json(json)
# print the JSON string representation of the object
print(GetCategoryVersionsResponse.to_json())

# convert the object into a dict
get_category_versions_response_dict = get_category_versions_response_instance.to_dict()
# create an instance of GetCategoryVersionsResponse from a dict
get_category_versions_response_from_dict = GetCategoryVersionsResponse.from_dict(get_category_versions_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


