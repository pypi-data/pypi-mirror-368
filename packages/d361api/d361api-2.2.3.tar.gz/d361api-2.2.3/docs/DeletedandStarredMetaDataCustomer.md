# DeletedandStarredMetaDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The file ID | [optional] 
**file_name** | **str** | The file name | [optional] 
**file_type** | **str** | The file type | [optional] 
**file_url** | **str** | The file URL | [optional] 
**updated_on** | **datetime** | The date the file was uploaded | [optional] 
**updated_by** | **str** | The ID of user who uploaded the file | [optional] 
**size** | **str** | The file size | [optional] 
**height** | **str** | The file height | [optional] 
**width** | **str** | The file width | [optional] 
**title** | **str** | The file title | [optional] 
**alternative_text** | **str** | The alternative text | [optional] 
**is_starred** | **bool** | This denotes the file is starred or not | [optional] 
**parent_folder_id** | **str** | The parent folder ID | [optional] 
**tag_ids** | **List[str]** | The tagIds associated with the file | [optional] 

## Example

```python
from d361api.d361api.deletedand_starred_meta_data_customer import DeletedandStarredMetaDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of DeletedandStarredMetaDataCustomer from a JSON string
deletedand_starred_meta_data_customer_instance = DeletedandStarredMetaDataCustomer.from_json(json)
# print the JSON string representation of the object
print(DeletedandStarredMetaDataCustomer.to_json())

# convert the object into a dict
deletedand_starred_meta_data_customer_dict = deletedand_starred_meta_data_customer_instance.to_dict()
# create an instance of DeletedandStarredMetaDataCustomer from a dict
deletedand_starred_meta_data_customer_from_dict = DeletedandStarredMetaDataCustomer.from_dict(deletedand_starred_meta_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


