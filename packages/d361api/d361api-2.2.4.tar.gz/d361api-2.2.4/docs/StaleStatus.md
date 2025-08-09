# StaleStatus


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**article_stale_status** | [**ArticleStaleStatus**](ArticleStaleStatus.md) | The status of the article: 0 - None, 1 - New, 2 - Updated, 3 - Custom | [optional] 
**stale_reason** | **str** |  | [optional] 
**expired_at** | **datetime** |  | [optional] 

## Example

```python
from d361api.d361api.stale_status import StaleStatus

# TODO update the JSON string below
json = "{}"
# create an instance of StaleStatus from a JSON string
stale_status_instance = StaleStatus.from_json(json)
# print the JSON string representation of the object
print(StaleStatus.to_json())

# convert the object into a dict
stale_status_dict = stale_status_instance.to_dict()
# create an instance of StaleStatus from a dict
stale_status_from_dict = StaleStatus.from_dict(stale_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


