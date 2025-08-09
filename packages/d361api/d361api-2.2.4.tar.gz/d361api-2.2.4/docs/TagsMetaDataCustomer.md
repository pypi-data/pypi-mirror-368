# TagsMetaDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The tag ID | [optional] 
**tag_name** | **str** | The tag name | [optional] 

## Example

```python
from d361api.d361api.tags_meta_data_customer import TagsMetaDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of TagsMetaDataCustomer from a JSON string
tags_meta_data_customer_instance = TagsMetaDataCustomer.from_json(json)
# print the JSON string representation of the object
print(TagsMetaDataCustomer.to_json())

# convert the object into a dict
tags_meta_data_customer_dict = tags_meta_data_customer_instance.to_dict()
# create an instance of TagsMetaDataCustomer from a dict
tags_meta_data_customer_from_dict = TagsMetaDataCustomer.from_dict(tags_meta_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


