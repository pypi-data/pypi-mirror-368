# Title


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** | Markup text with occurrences highlighted. | [optional] 
**match_level** | **str** | Indicates how well the attribute matched the search query. Can be: none, partial, full | [optional] 
**fully_highlighted** | **bool** |  | [optional] 
**matched_words** | **List[str]** | List of words from the query that matched the object. | [optional] 

## Example

```python
from d361api.d361api.title import Title

# TODO update the JSON string below
json = "{}"
# create an instance of Title from a JSON string
title_instance = Title.from_json(json)
# print the JSON string representation of the object
print(Title.to_json())

# convert the object into a dict
title_dict = title_instance.to_dict()
# create an instance of Title from a dict
title_from_dict = Title.from_dict(title_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


