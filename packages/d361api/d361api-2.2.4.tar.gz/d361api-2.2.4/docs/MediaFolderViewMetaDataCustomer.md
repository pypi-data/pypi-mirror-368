# MediaFolderViewMetaDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the folder in Drive | [optional] 
**title** | **str** | This  folder title | [optional] 
**order** | **int** | The order of the folder | [optional] 
**parent_folder_id** | **str** | The parent folder ID | [optional] 
**files** | [**List[MediaFilesMetaDataCustomer]**](MediaFilesMetaDataCustomer.md) | The files associated to the folder | [optional] 
**icon** | **str** | The icon of the folder | [optional] 
**items_count** | **int** | Subfolder count in the folder | [optional] 
**updated_on** | **datetime** | The date the folder was created | [optional] 
**updated_by** | **str** | The ID of the user that created the folder | [optional] 
**is_starred** | **bool** | This denotes the folder is starred or not | [optional] 
**folder_color** | **str** | The folder color | [optional] 
**files_count** | **int** | The folder file count | [optional] 
**sub_folders** | [**List[MediaFoldersDataCustomer]**](MediaFoldersDataCustomer.md) | Sub folders of the media folder | [optional] 

## Example

```python
from d361api.d361api.media_folder_view_meta_data_customer import MediaFolderViewMetaDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of MediaFolderViewMetaDataCustomer from a JSON string
media_folder_view_meta_data_customer_instance = MediaFolderViewMetaDataCustomer.from_json(json)
# print the JSON string representation of the object
print(MediaFolderViewMetaDataCustomer.to_json())

# convert the object into a dict
media_folder_view_meta_data_customer_dict = media_folder_view_meta_data_customer_instance.to_dict()
# create an instance of MediaFolderViewMetaDataCustomer from a dict
media_folder_view_meta_data_customer_from_dict = MediaFolderViewMetaDataCustomer.from_dict(media_folder_view_meta_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


