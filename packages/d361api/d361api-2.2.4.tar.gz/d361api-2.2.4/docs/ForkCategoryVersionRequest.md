# ForkCategoryVersionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version_number** | **int** | The version number of the category page | 
**user_id** | **str** | The ID of the team account | 
**lang_code** | **str** | Language code of the category | 

## Example

```python
from d361api.d361api.fork_category_version_request import ForkCategoryVersionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ForkCategoryVersionRequest from a JSON string
fork_category_version_request_instance = ForkCategoryVersionRequest.from_json(json)
# print the JSON string representation of the object
print(ForkCategoryVersionRequest.to_json())

# convert the object into a dict
fork_category_version_request_dict = fork_category_version_request_instance.to_dict()
# create an instance of ForkCategoryVersionRequest from a dict
fork_category_version_request_from_dict = ForkCategoryVersionRequest.from_dict(fork_category_version_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


