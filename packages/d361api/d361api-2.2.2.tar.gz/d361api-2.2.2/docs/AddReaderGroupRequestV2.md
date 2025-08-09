# AddReaderGroupRequestV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** | The name of the reader group | 
**description** | **str** | Access level of the reader group | [optional] 
**associated_readers** | **List[str]** | Description of the reader group | [optional] 
**access_scope** | [**AddUpdateAccessScopeCustomerV2**](AddUpdateAccessScopeCustomerV2.md) | List of reader IDs to be associated with the reader group | 
**associated_invited_sso_users** | **List[str]** | List of invitation IDs to be associated with this reader group. Applicable only for SSO readers. | [optional] 

## Example

```python
from d361api.d361api.add_reader_group_request_v2 import AddReaderGroupRequestV2

# TODO update the JSON string below
json = "{}"
# create an instance of AddReaderGroupRequestV2 from a JSON string
add_reader_group_request_v2_instance = AddReaderGroupRequestV2.from_json(json)
# print the JSON string representation of the object
print(AddReaderGroupRequestV2.to_json())

# convert the object into a dict
add_reader_group_request_v2_dict = add_reader_group_request_v2_instance.to_dict()
# create an instance of AddReaderGroupRequestV2 from a dict
add_reader_group_request_v2_from_dict = AddReaderGroupRequestV2.from_dict(add_reader_group_request_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


