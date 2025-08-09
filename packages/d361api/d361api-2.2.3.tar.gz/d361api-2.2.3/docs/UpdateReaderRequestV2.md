# UpdateReaderRequestV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** | The first name of the reader | [optional] 
**last_name** | **str** | The last name of the reader | [optional] 
**associated_reader_groups** | **List[str]** | List of reader group IDs. If the value is null or not given, then the reader would be removed from all associated reader groups. | 
**access_scope** | [**AddUpdateAccessScopeCustomerV2**](AddUpdateAccessScopeCustomerV2.md) | Access level of the reader. 0-None, 1-Category, 2-Version, 3-Project, 4-Language. | 
**is_invitation_id** | **bool** | Applicable only for Single Sign-On readers. Set this property to true, if the reader is a Single Sign-On reader who hasn&#39;t logged in to the application yet. | [optional] 
**sso_user_type** | [**SSOUserTypes**](SSOUserTypes.md) | SSO user type 0 - Normal user, 1 - SSO user, 2 - Invited SSO user | [optional] 

## Example

```python
from d361api.d361api.update_reader_request_v2 import UpdateReaderRequestV2

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateReaderRequestV2 from a JSON string
update_reader_request_v2_instance = UpdateReaderRequestV2.from_json(json)
# print the JSON string representation of the object
print(UpdateReaderRequestV2.to_json())

# convert the object into a dict
update_reader_request_v2_dict = update_reader_request_v2_instance.to_dict()
# create an instance of UpdateReaderRequestV2 from a dict
update_reader_request_v2_from_dict = UpdateReaderRequestV2.from_dict(update_reader_request_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


