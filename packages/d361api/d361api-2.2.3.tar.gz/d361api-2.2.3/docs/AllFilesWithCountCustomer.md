# AllFilesWithCountCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**all_files** | [**List[DeletedandStarredMetaDataCustomer]**](DeletedandStarredMetaDataCustomer.md) | Search file items from drive | [optional] 
**count** | **int** | Total file count | [optional] 

## Example

```python
from d361api.d361api.all_files_with_count_customer import AllFilesWithCountCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of AllFilesWithCountCustomer from a JSON string
all_files_with_count_customer_instance = AllFilesWithCountCustomer.from_json(json)
# print the JSON string representation of the object
print(AllFilesWithCountCustomer.to_json())

# convert the object into a dict
all_files_with_count_customer_dict = all_files_with_count_customer_instance.to_dict()
# create an instance of AllFilesWithCountCustomer from a dict
all_files_with_count_customer_from_dict = AllFilesWithCountCustomer.from_dict(all_files_with_count_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


