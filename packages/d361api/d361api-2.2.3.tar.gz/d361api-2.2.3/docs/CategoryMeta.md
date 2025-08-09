# CategoryMeta


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**language_id** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**version_id** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.category_meta import CategoryMeta

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryMeta from a JSON string
category_meta_instance = CategoryMeta.from_json(json)
# print the JSON string representation of the object
print(CategoryMeta.to_json())

# convert the object into a dict
category_meta_dict = category_meta_instance.to_dict()
# create an instance of CategoryMeta from a dict
category_meta_from_dict = CategoryMeta.from_dict(category_meta_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


