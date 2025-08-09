# MediaFilesMetaDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The file ID | 
**file_name** | **str** | The file name | [optional] 
**file_type** | **str** | The file tyoe | [optional] 
**file_url** | **str** | The file URL | [optional] 
**updated_on** | **datetime** | The date file was modified | [optional] 
**updated_by** | **str** | The ID of the user who uploaded the file | [optional] 
**size** | **str** | The file size | [optional] 
**tags** | [**List[TagsMetaDataCustomer]**](TagsMetaDataCustomer.md) | The tags associated with file | [optional] 
**is_starred** | **bool** | This denotes the file is starred or not | [optional] 

## Example

```python
from d361api.d361api.media_files_meta_data_customer import MediaFilesMetaDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of MediaFilesMetaDataCustomer from a JSON string
media_files_meta_data_customer_instance = MediaFilesMetaDataCustomer.from_json(json)
# print the JSON string representation of the object
print(MediaFilesMetaDataCustomer.to_json())

# convert the object into a dict
media_files_meta_data_customer_dict = media_files_meta_data_customer_instance.to_dict()
# create an instance of MediaFilesMetaDataCustomer from a dict
media_files_meta_data_customer_from_dict = MediaFilesMetaDataCustomer.from_dict(media_files_meta_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


