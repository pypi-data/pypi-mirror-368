# ApiReferencePublishRequestCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_reference_id** | **str** | The ID of the API reference | 
**project_version_id** | **str** | The ID of the project version | 
**user_id** | **str** | The ID of the team account | 

## Example

```python
from d361api.d361api.api_reference_publish_request_customer import ApiReferencePublishRequestCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of ApiReferencePublishRequestCustomer from a JSON string
api_reference_publish_request_customer_instance = ApiReferencePublishRequestCustomer.from_json(json)
# print the JSON string representation of the object
print(ApiReferencePublishRequestCustomer.to_json())

# convert the object into a dict
api_reference_publish_request_customer_dict = api_reference_publish_request_customer_instance.to_dict()
# create an instance of ApiReferencePublishRequestCustomer from a dict
api_reference_publish_request_customer_from_dict = ApiReferencePublishRequestCustomer.from_dict(api_reference_publish_request_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


