# GetLogsDetailsResponseCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_reference_errors** | [**List[ApiLogs]**](ApiLogs.md) | Error log response | [optional] 
**api_reference_alerts** | [**List[ApiLogs]**](ApiLogs.md) | Alerts log response | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.get_logs_details_response_customer import GetLogsDetailsResponseCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of GetLogsDetailsResponseCustomer from a JSON string
get_logs_details_response_customer_instance = GetLogsDetailsResponseCustomer.from_json(json)
# print the JSON string representation of the object
print(GetLogsDetailsResponseCustomer.to_json())

# convert the object into a dict
get_logs_details_response_customer_dict = get_logs_details_response_customer_instance.to_dict()
# create an instance of GetLogsDetailsResponseCustomer from a dict
get_logs_details_response_customer_from_dict = GetLogsDetailsResponseCustomer.from_dict(get_logs_details_response_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


