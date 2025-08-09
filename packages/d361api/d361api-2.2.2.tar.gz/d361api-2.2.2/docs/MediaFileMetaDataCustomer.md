# MediaFileMetaDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Media file Id | 
**title** | **str** |  | [optional] 
**file_name** | **str** | The file name | [optional] 
**file_type** | **str** | The file type | [optional] 
**file_url** | **str** | The file URL | [optional] 
**updated_by** | **str** | The ID of the user who uploaded the file | [optional] 
**media_folder_id** | **str** | The parent Folder ID | [optional] 

## Example

```python
from d361api.d361api.media_file_meta_data_customer import MediaFileMetaDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of MediaFileMetaDataCustomer from a JSON string
media_file_meta_data_customer_instance = MediaFileMetaDataCustomer.from_json(json)
# print the JSON string representation of the object
print(MediaFileMetaDataCustomer.to_json())

# convert the object into a dict
media_file_meta_data_customer_dict = media_file_meta_data_customer_instance.to_dict()
# create an instance of MediaFileMetaDataCustomer from a dict
media_file_meta_data_customer_from_dict = MediaFileMetaDataCustomer.from_dict(media_file_meta_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


