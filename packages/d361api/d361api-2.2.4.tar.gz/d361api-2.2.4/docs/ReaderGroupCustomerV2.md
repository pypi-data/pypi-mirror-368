# ReaderGroupCustomerV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reader_group_id** | **str** | The ID of the reader group. | [optional] 
**title** | **str** | The name of the reader group. | [optional] 
**description** | **str** | Description of the reader group. | [optional] 
**associated_readers** | **List[str]** | List of reader IDs to be associated with this reader group. | [optional] 
**associated_invited_sso_users** | **List[str]** | List of reader invitation IDs. Applicable only for SSO readers. | [optional] 
**access_scope** | [**AccessScopeCustomerV2**](AccessScopeCustomerV2.md) | Access scope of this reader group. | [optional] 

## Example

```python
from d361api.d361api.reader_group_customer_v2 import ReaderGroupCustomerV2

# TODO update the JSON string below
json = "{}"
# create an instance of ReaderGroupCustomerV2 from a JSON string
reader_group_customer_v2_instance = ReaderGroupCustomerV2.from_json(json)
# print the JSON string representation of the object
print(ReaderGroupCustomerV2.to_json())

# convert the object into a dict
reader_group_customer_v2_dict = reader_group_customer_v2_instance.to_dict()
# create an instance of ReaderGroupCustomerV2 from a dict
reader_group_customer_v2_from_dict = ReaderGroupCustomerV2.from_dict(reader_group_customer_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


