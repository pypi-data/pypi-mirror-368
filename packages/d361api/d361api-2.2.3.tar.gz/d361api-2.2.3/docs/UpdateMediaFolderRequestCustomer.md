# UpdateMediaFolderRequestCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The new name for the folder being updated | [optional] 
**order** | **int** | The order of the folder | [optional] 
**folder_color** | **str** | The color of the folder - should be in hexadecimal color code format | [optional] 
**is_starred** | **bool** | To update the folder as starred | [optional] 

## Example

```python
from d361api.d361api.update_media_folder_request_customer import UpdateMediaFolderRequestCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateMediaFolderRequestCustomer from a JSON string
update_media_folder_request_customer_instance = UpdateMediaFolderRequestCustomer.from_json(json)
# print the JSON string representation of the object
print(UpdateMediaFolderRequestCustomer.to_json())

# convert the object into a dict
update_media_folder_request_customer_dict = update_media_folder_request_customer_instance.to_dict()
# create an instance of UpdateMediaFolderRequestCustomer from a dict
update_media_folder_request_customer_from_dict = UpdateMediaFolderRequestCustomer.from_dict(update_media_folder_request_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


