# AddMediaFolderRequestCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** | The title of the folder | [optional] 
**parent_folder_id** | **str** | The parent media folder ID | [optional] 
**user_id** | **str** | The ID of the user | [optional] 
**order** | **int** | The order of the folder | [optional] 

## Example

```python
from d361api.d361api.add_media_folder_request_customer import AddMediaFolderRequestCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of AddMediaFolderRequestCustomer from a JSON string
add_media_folder_request_customer_instance = AddMediaFolderRequestCustomer.from_json(json)
# print the JSON string representation of the object
print(AddMediaFolderRequestCustomer.to_json())

# convert the object into a dict
add_media_folder_request_customer_dict = add_media_folder_request_customer_instance.to_dict()
# create an instance of AddMediaFolderRequestCustomer from a dict
add_media_folder_request_customer_from_dict = AddMediaFolderRequestCustomer.from_dict(add_media_folder_request_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


