# UpdateCategoryContentCustomerResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**CategoryVersionDataCustomer**](CategoryVersionDataCustomer.md) | category version data | [optional] 
**extension_data** | **object** | Extension data for customer API response | [optional] 
**success** | **bool** | Indicates the status of the API response. A value of true signifies that the request was successfully processed, while false indicates a failure or error occurred. | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | A list of errors encountered during the API request. Each error object provides details about the problem, including an error code and a message explaining the issue. This field is populated when the request fails or encounters issues. | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | A list of warnings generated during the API request. These are non-critical issues or recommendations that might affect the request but won&#39;t stop it from processing. Each warning object provides a message to inform the user of potential problems. | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Contains additional non-critical information relevant to the request or response. This field provides extra details that might assist in understanding the context of the API response but is not essential for processing. | [optional] 

## Example

```python
from d361api.d361api.update_category_content_customer_response import UpdateCategoryContentCustomerResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateCategoryContentCustomerResponse from a JSON string
update_category_content_customer_response_instance = UpdateCategoryContentCustomerResponse.from_json(json)
# print the JSON string representation of the object
print(UpdateCategoryContentCustomerResponse.to_json())

# convert the object into a dict
update_category_content_customer_response_dict = update_category_content_customer_response_instance.to_dict()
# create an instance of UpdateCategoryContentCustomerResponse from a dict
update_category_content_customer_response_from_dict = UpdateCategoryContentCustomerResponse.from_dict(update_category_content_customer_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


