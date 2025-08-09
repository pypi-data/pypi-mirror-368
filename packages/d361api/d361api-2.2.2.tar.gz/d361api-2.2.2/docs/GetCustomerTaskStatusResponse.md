# GetCustomerTaskStatusResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**task_status** | [**DriveTaskStatus**](DriveTaskStatus.md) |  | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.get_customer_task_status_response import GetCustomerTaskStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetCustomerTaskStatusResponse from a JSON string
get_customer_task_status_response_instance = GetCustomerTaskStatusResponse.from_json(json)
# print the JSON string representation of the object
print(GetCustomerTaskStatusResponse.to_json())

# convert the object into a dict
get_customer_task_status_response_dict = get_customer_task_status_response_instance.to_dict()
# create an instance of GetCustomerTaskStatusResponse from a dict
get_customer_task_status_response_from_dict = GetCustomerTaskStatusResponse.from_dict(get_customer_task_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


