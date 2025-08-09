# FormEditableProperties


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**element_name** | **str** |  | [optional] 
**element_type** | [**EditableElementTypes**](EditableElementTypes.md) |  | [optional] 
**label** | **str** |  | [optional] 
**value** | **str** |  | [optional] 
**view_form_control** | [**ViewFormControl**](ViewFormControl.md) |  | [optional] 
**editable_properties** | [**FormEditableProperties**](FormEditableProperties.md) |  | [optional] 
**element_guid** | **str** |  | [optional] 
**children** | [**List[FormEditableProperties]**](FormEditableProperties.md) |  | [optional] 
**edit_component_style_properties** | **Dict[str, object]** |  | [optional] 
**edit_component_properties** | **Dict[str, object]** |  | [optional] 

## Example

```python
from d361api.d361api.form_editable_properties import FormEditableProperties

# TODO update the JSON string below
json = "{}"
# create an instance of FormEditableProperties from a JSON string
form_editable_properties_instance = FormEditableProperties.from_json(json)
# print the JSON string representation of the object
print(FormEditableProperties.to_json())

# convert the object into a dict
form_editable_properties_dict = form_editable_properties_instance.to_dict()
# create an instance of FormEditableProperties from a dict
form_editable_properties_from_dict = FormEditableProperties.from_dict(form_editable_properties_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


