# AddUserData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Newly added user Id | [optional] 

## Example

```python
from d361api.d361api.add_user_data import AddUserData

# TODO update the JSON string below
json = "{}"
# create an instance of AddUserData from a JSON string
add_user_data_instance = AddUserData.from_json(json)
# print the JSON string representation of the object
print(AddUserData.to_json())

# convert the object into a dict
add_user_data_dict = add_user_data_instance.to_dict()
# create an instance of AddUserData from a dict
add_user_data_from_dict = AddUserData.from_dict(add_user_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


