# UIElement


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**element_type** | [**UIElementType**](UIElementType.md) |  | [optional] 
**element_name** | **str** |  | [optional] 
**element_guid** | **str** |  | [optional] 
**display_name** | **str** |  | [optional] 
**view_styles** | **Dict[str, object]** |  | [optional] 
**view_properties** | **Dict[str, object]** |  | [optional] 
**editable_properties** | [**List[FormEditableProperties]**](FormEditableProperties.md) |  | [optional] 
**children** | [**List[UIElement]**](UIElement.md) |  | [optional] 

## Example

```python
from d361api.d361api.ui_element import UIElement

# TODO update the JSON string below
json = "{}"
# create an instance of UIElement from a JSON string
ui_element_instance = UIElement.from_json(json)
# print the JSON string representation of the object
print(UIElement.to_json())

# convert the object into a dict
ui_element_dict = ui_element_instance.to_dict()
# create an instance of UIElement from a dict
ui_element_from_dict = UIElement.from_dict(ui_element_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


