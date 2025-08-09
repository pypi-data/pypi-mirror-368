# CategorySimpleData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the category | [optional] 
**name** | **str** | Name of the category | [optional] 
**order** | **int** | The position inside the parent category | [optional] 
**icon** | **str** | Unicode representation of the icon | [optional] 

## Example

```python
from d361api.d361api.category_simple_data import CategorySimpleData

# TODO update the JSON string below
json = "{}"
# create an instance of CategorySimpleData from a JSON string
category_simple_data_instance = CategorySimpleData.from_json(json)
# print the JSON string representation of the object
print(CategorySimpleData.to_json())

# convert the object into a dict
category_simple_data_dict = category_simple_data_instance.to_dict()
# create an instance of CategorySimpleData from a dict
category_simple_data_from_dict = CategorySimpleData.from_dict(category_simple_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


