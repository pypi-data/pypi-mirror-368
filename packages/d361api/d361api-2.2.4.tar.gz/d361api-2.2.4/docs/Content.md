# Content


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** | Markup text with occurrences highlighted. | [optional] 
**match_level** | **str** | Indicates how well the attribute matched the search query. Can be: none, partial, full | [optional] 

## Example

```python
from d361api.d361api.content import Content

# TODO update the JSON string below
json = "{}"
# create an instance of Content from a JSON string
content_instance = Content.from_json(json)
# print the JSON string representation of the object
print(Content.to_json())

# convert the object into a dict
content_dict = content_instance.to_dict()
# create an instance of Content from a dict
content_from_dict = Content.from_dict(content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


