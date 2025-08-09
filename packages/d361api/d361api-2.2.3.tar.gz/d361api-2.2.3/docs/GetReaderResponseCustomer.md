# GetReaderResponseCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reader_id** | **str** | The ID of the reader. | [optional] 
**first_name** | **str** | The first name of the reader. | [optional] 
**last_name** | **str** | The last name of the reader. | [optional] 
**email** | **str** | Email address of the reader. | [optional] 
**access_scope** | [**AccessScopeCustomerV2**](AccessScopeCustomerV2.md) | The access scope of the reader. | [optional] 
**associated_reader_groups** | **List[str]** | An array of the group IDs the reader is associated with. | [optional] 
**is_invite_sso_user** | **bool** | Applicable only for SSO readers. If true, it indicates that an invitation has been sent to the reader, but the reader hasn&#39;t accepted the invitation yet. | [optional] 
**last_login_at** | **datetime** | The last login date and time by the reader. | [optional] 

## Example

```python
from d361api.d361api.get_reader_response_customer import GetReaderResponseCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of GetReaderResponseCustomer from a JSON string
get_reader_response_customer_instance = GetReaderResponseCustomer.from_json(json)
# print the JSON string representation of the object
print(GetReaderResponseCustomer.to_json())

# convert the object into a dict
get_reader_response_customer_dict = get_reader_response_customer_instance.to_dict()
# create an instance of GetReaderResponseCustomer from a dict
get_reader_response_customer_from_dict = GetReaderResponseCustomer.from_dict(get_reader_response_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


