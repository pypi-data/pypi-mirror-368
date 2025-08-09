# ViewFormControl


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**property_key** | **str** |  | [optional] 
**is_children** | **int** |  | [optional] 
**view_type** | **str** |  | [optional] 
**element_name** | **str** |  | [optional] 
**is_children_root** | **bool** |  | [optional] 
**element_type** | **str** |  | [optional] 
**inverted_value** | **bool** |  | [optional] 
**is_dirty** | **bool** |  | [optional] 

## Example

```python
from d361api.d361api.view_form_control import ViewFormControl

# TODO update the JSON string below
json = "{}"
# create an instance of ViewFormControl from a JSON string
view_form_control_instance = ViewFormControl.from_json(json)
# print the JSON string representation of the object
print(ViewFormControl.to_json())

# convert the object into a dict
view_form_control_dict = view_form_control_instance.to_dict()
# create an instance of ViewFormControl from a dict
view_form_control_from_dict = ViewFormControl.from_dict(view_form_control_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


