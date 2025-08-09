# UpdateCategoryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**CategorySimpleData**](CategorySimpleData.md) | category simple data | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.update_category_response import UpdateCategoryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateCategoryResponse from a JSON string
update_category_response_instance = UpdateCategoryResponse.from_json(json)
# print the JSON string representation of the object
print(UpdateCategoryResponse.to_json())

# convert the object into a dict
update_category_response_dict = update_category_response_instance.to_dict()
# create an instance of UpdateCategoryResponse from a dict
update_category_response_from_dict = UpdateCategoryResponse.from_dict(update_category_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


