# TrophyStatus


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first** | **bool** |  | [optional] 
**second** | **bool** |  | [optional] 
**third** | **bool** |  | [optional] 
**fourth** | **bool** |  | [optional] 

## Example

```python
from d361api.d361api.trophy_status import TrophyStatus

# TODO update the JSON string below
json = "{}"
# create an instance of TrophyStatus from a JSON string
trophy_status_instance = TrophyStatus.from_json(json)
# print the JSON string representation of the object
print(TrophyStatus.to_json())

# convert the object into a dict
trophy_status_dict = trophy_status_instance.to_dict()
# create an instance of TrophyStatus from a dict
trophy_status_from_dict = TrophyStatus.from_dict(trophy_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


