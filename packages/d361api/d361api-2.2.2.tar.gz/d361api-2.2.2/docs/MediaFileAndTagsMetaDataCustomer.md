# MediaFileAndTagsMetaDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The file ID | 
**file_name** | **str** | The file name | [optional] 
**file_type** | **str** | The file type | [optional] 
**file_url** | **str** | The file URL | [optional] 
**updated_on** | **datetime** | The date the file was uploaded | [optional] 
**updated_by** | **str** | The ID of user who uploaded the file | [optional] 
**size** | **str** | The file size | [optional] 
**height** | **str** | The file height | [optional] 
**width** | **str** | The file width | [optional] 
**parent_folder_id** | **str** | The parent folder ID | [optional] 
**title** | **str** | The file title | [optional] 
**alternative_text** | **str** | The file alternative text | [optional] 
**tags** | [**List[TagsMetaDataCustomer]**](TagsMetaDataCustomer.md) | The tags associated with the file | [optional] 
**thumbnail_url** | **str** | The thumbnail URL | [optional] 
**is_starred** | **bool** | This denotes the file is starred or not | [optional] 

## Example

```python
from d361api.d361api.media_file_and_tags_meta_data_customer import MediaFileAndTagsMetaDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of MediaFileAndTagsMetaDataCustomer from a JSON string
media_file_and_tags_meta_data_customer_instance = MediaFileAndTagsMetaDataCustomer.from_json(json)
# print the JSON string representation of the object
print(MediaFileAndTagsMetaDataCustomer.to_json())

# convert the object into a dict
media_file_and_tags_meta_data_customer_dict = media_file_and_tags_meta_data_customer_instance.to_dict()
# create an instance of MediaFileAndTagsMetaDataCustomer from a dict
media_file_and_tags_meta_data_customer_from_dict = MediaFileAndTagsMetaDataCustomer.from_dict(media_file_and_tags_meta_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


