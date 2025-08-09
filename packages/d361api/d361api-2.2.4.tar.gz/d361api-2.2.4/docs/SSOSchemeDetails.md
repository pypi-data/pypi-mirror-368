# SSOSchemeDetails


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**sso_name** | **str** |  | [optional] 
**project_id** | **str** |  | [optional] 
**scheme_name** | **str** |  | [optional] 
**display_name** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.sso_scheme_details import SSOSchemeDetails

# TODO update the JSON string below
json = "{}"
# create an instance of SSOSchemeDetails from a JSON string
sso_scheme_details_instance = SSOSchemeDetails.from_json(json)
# print the JSON string representation of the object
print(SSOSchemeDetails.to_json())

# convert the object into a dict
sso_scheme_details_dict = sso_scheme_details_instance.to_dict()
# create an instance of SSOSchemeDetails from a dict
sso_scheme_details_from_dict = SSOSchemeDetails.from_dict(sso_scheme_details_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


