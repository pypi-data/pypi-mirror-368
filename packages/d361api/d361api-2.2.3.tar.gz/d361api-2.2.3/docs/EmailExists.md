# EmailExists


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exists** | **bool** | A boolean flag indicating if the user exists in the project or not | [optional] 
**user_id** | **str** | The user ID associated with the email. Will be null if the email address does not exist in the project. | [optional] 

## Example

```python
from d361api.d361api.email_exists import EmailExists

# TODO update the JSON string below
json = "{}"
# create an instance of EmailExists from a JSON string
email_exists_instance = EmailExists.from_json(json)
# print the JSON string representation of the object
print(EmailExists.to_json())

# convert the object into a dict
email_exists_dict = email_exists_instance.to_dict()
# create an instance of EmailExists from a dict
email_exists_from_dict = EmailExists.from_dict(email_exists_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


