# Snippetresult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**Content**](Content.md) |  | [optional] 

## Example

```python
from d361api.d361api.snippetresult import Snippetresult

# TODO update the JSON string below
json = "{}"
# create an instance of Snippetresult from a JSON string
snippetresult_instance = Snippetresult.from_json(json)
# print the JSON string representation of the object
print(Snippetresult.to_json())

# convert the object into a dict
snippetresult_dict = snippetresult_instance.to_dict()
# create an instance of Snippetresult from a dict
snippetresult_from_dict = Snippetresult.from_dict(snippetresult_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


