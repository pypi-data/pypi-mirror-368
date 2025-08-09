# MediaFoldersDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | This is the folder Id | [optional] 
**title** | **str** | This is the folder title | [optional] 
**parent_folder_id** | **str** | The parent folder ID | [optional] 
**sub_folders** | [**List[MediaFoldersDataCustomer]**](MediaFoldersDataCustomer.md) | The sub folders in the parent | [optional] 
**items_count** | **int** | The items in the folder | [optional] 
**updated_by** | **str** | The ID of the user that created the folder | [optional] 
**updated_on** | **datetime** | The date the folder was created | [optional] 
**order** | **int** | The order of the folder | [optional] 
**is_starred** | **bool** | This denotes the folder is starred or not | [optional] 

## Example

```python
from d361api.d361api.media_folders_data_customer import MediaFoldersDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of MediaFoldersDataCustomer from a JSON string
media_folders_data_customer_instance = MediaFoldersDataCustomer.from_json(json)
# print the JSON string representation of the object
print(MediaFoldersDataCustomer.to_json())

# convert the object into a dict
media_folders_data_customer_dict = media_folders_data_customer_instance.to_dict()
# create an instance of MediaFoldersDataCustomer from a dict
media_folders_data_customer_from_dict = MediaFoldersDataCustomer.from_dict(media_folders_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


