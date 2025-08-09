# UpdateReaderGroupRequestV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** | The name of the reader group. | 
**description** | **str** | Description of the reader group. | [optional] 
**associated_readers** | **List[str]** |  List of reader IDs to be associated with this reader group.  Note: Reader IDs that were previously associated but not present in this list during the update will be dissociated from this reader group. | [optional] 
**access_scope** | [**AddUpdateAccessScopeCustomerV2**](AddUpdateAccessScopeCustomerV2.md) | Access level of this reader group. | 
**associated_invited_sso_users** | **List[str]** |  List of invitation IDs to be associated with this reader group.  Note: Invitation IDs that were previously associated but not present in this list during the update will be disassociated from this reader group. | [optional] 

## Example

```python
from d361api.d361api.update_reader_group_request_v2 import UpdateReaderGroupRequestV2

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateReaderGroupRequestV2 from a JSON string
update_reader_group_request_v2_instance = UpdateReaderGroupRequestV2.from_json(json)
# print the JSON string representation of the object
print(UpdateReaderGroupRequestV2.to_json())

# convert the object into a dict
update_reader_group_request_v2_dict = update_reader_group_request_v2_instance.to_dict()
# create an instance of UpdateReaderGroupRequestV2 from a dict
update_reader_group_request_v2_from_dict = UpdateReaderGroupRequestV2.from_dict(update_reader_group_request_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


