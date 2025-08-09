# ReaderGroupCustomerV2ListCustomerApiResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**result** | [**List[ReaderGroupCustomerV2]**](ReaderGroupCustomerV2.md) | Customer API response data | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.reader_group_customer_v2_list_customer_api_response import ReaderGroupCustomerV2ListCustomerApiResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ReaderGroupCustomerV2ListCustomerApiResponse from a JSON string
reader_group_customer_v2_list_customer_api_response_instance = ReaderGroupCustomerV2ListCustomerApiResponse.from_json(json)
# print the JSON string representation of the object
print(ReaderGroupCustomerV2ListCustomerApiResponse.to_json())

# convert the object into a dict
reader_group_customer_v2_list_customer_api_response_dict = reader_group_customer_v2_list_customer_api_response_instance.to_dict()
# create an instance of ReaderGroupCustomerV2ListCustomerApiResponse from a dict
reader_group_customer_v2_list_customer_api_response_from_dict = ReaderGroupCustomerV2ListCustomerApiResponse.from_dict(reader_group_customer_v2_list_customer_api_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


