# AddReaderRequestV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** | The first name of the reader | [optional] 
**last_name** | **str** | The last name of the reader | [optional] 
**email_id** | **str** | The Email address of the reader | 
**associated_reader_groups** | **List[str]** | List of reader group IDs | [optional] 
**access_scope** | [**AddUpdateAccessScopeCustomerV2**](AddUpdateAccessScopeCustomerV2.md) | If access scope is not given, then 0-None access level will be assigned | [optional] 
**is_sso_user** | **bool** | Specify if the reader is a Single Sign-On user or not | [optional] 
**scheme_name** | **str** | Specify to add the reader to the specific scheme name, if the reader is a Single Sign-On user. If the scheme name is not provided, then the reader will be added to the default scheme. | [optional] 
**skip_sso_invitation_email** | **bool** | If the value is true, then the invitation email will not be sent to the reader. Applicable only for a Single Sign-On reader. | [optional] 
**invited_by** | **str** | The ID of an existing team account. The name of this team account will be mentioned in the invitation email. | 

## Example

```python
from d361api.d361api.add_reader_request_v2 import AddReaderRequestV2

# TODO update the JSON string below
json = "{}"
# create an instance of AddReaderRequestV2 from a JSON string
add_reader_request_v2_instance = AddReaderRequestV2.from_json(json)
# print the JSON string representation of the object
print(AddReaderRequestV2.to_json())

# convert the object into a dict
add_reader_request_v2_dict = add_reader_request_v2_instance.to_dict()
# create an instance of AddReaderRequestV2 from a dict
add_reader_request_v2_from_dict = AddReaderRequestV2.from_dict(add_reader_request_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


