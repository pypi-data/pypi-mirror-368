# ProjectVersionCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the project version | [optional] 
**version_number** | **float** | Project version number | [optional] 
**base_version_number** | **float** | The version number from which this version is derived | [optional] 
**version_code_name** | **str** | Custom version name | [optional] 
**is_main_version** | **bool** | \&quot;True\&quot; if this version is the main version after loading documentation | [optional] 
**is_beta** | **bool** | \&quot;True\&quot; if this version is marked as Beta | [optional] 
**is_public** | **bool** | \&quot;True\&quot; if this version is visible to the public | [optional] 
**is_deprecated** | **bool** | \&quot;True\&quot; if this version is marked as deprecated | [optional] 
**created_at** | **datetime** | The date and time the version was created | [optional] 
**modified_at** | **datetime** | The last date and time the version was modified | [optional] 
**language_versions** | [**List[Language]**](Language.md) |  | [optional] 
**slug** | **str** |  | [optional] 
**order** | **int** |  | [optional] 
**version_type** | [**ProjectVersionTypeCustomer**](ProjectVersionTypeCustomer.md) | 0 - KB workspace ; 1 - API Reference workspace; | [optional] 

## Example

```python
from d361api.d361api.project_version_customer import ProjectVersionCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectVersionCustomer from a JSON string
project_version_customer_instance = ProjectVersionCustomer.from_json(json)
# print the JSON string representation of the object
print(ProjectVersionCustomer.to_json())

# convert the object into a dict
project_version_customer_dict = project_version_customer_instance.to_dict()
# create an instance of ProjectVersionCustomer from a dict
project_version_customer_from_dict = ProjectVersionCustomer.from_dict(project_version_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


