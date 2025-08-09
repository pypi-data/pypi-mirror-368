# MediaFolderMetaDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**media_folder_id** | **str** | The folder ID | [optional] 
**media_folder_title** | **str** | The folder title | [optional] 
**order** | **int** | The folder order | [optional] 
**icon** | **str** | The folder icon | [optional] 
**updated_on** | **datetime** | The date the file was modified | [optional] 
**folder_color** | **str** | The folder color | [optional] 
**is_starred** | **bool** | This denotes the file is starred or not | [optional] 
**updated_by** | **str** | The ID of the user who uploaded the folder | [optional] 
**parent_media_folder_id** | **str** | The parent folder ID | [optional] 

## Example

```python
from d361api.d361api.media_folder_meta_data_customer import MediaFolderMetaDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of MediaFolderMetaDataCustomer from a JSON string
media_folder_meta_data_customer_instance = MediaFolderMetaDataCustomer.from_json(json)
# print the JSON string representation of the object
print(MediaFolderMetaDataCustomer.to_json())

# convert the object into a dict
media_folder_meta_data_customer_dict = media_folder_meta_data_customer_instance.to_dict()
# create an instance of MediaFolderMetaDataCustomer from a dict
media_folder_meta_data_customer_from_dict = MediaFolderMetaDataCustomer.from_dict(media_folder_meta_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


