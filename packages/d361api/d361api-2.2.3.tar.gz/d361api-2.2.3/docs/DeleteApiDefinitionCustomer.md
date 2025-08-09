# DeleteApiDefinitionCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_reference_id** | **str** | The ID of the API reference | [optional] 
**details** | **str** | Status message | [optional] 

## Example

```python
from d361api.d361api.delete_api_definition_customer import DeleteApiDefinitionCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteApiDefinitionCustomer from a JSON string
delete_api_definition_customer_instance = DeleteApiDefinitionCustomer.from_json(json)
# print the JSON string representation of the object
print(DeleteApiDefinitionCustomer.to_json())

# convert the object into a dict
delete_api_definition_customer_dict = delete_api_definition_customer_instance.to_dict()
# create an instance of DeleteApiDefinitionCustomer from a dict
delete_api_definition_customer_from_dict = DeleteApiDefinitionCustomer.from_dict(delete_api_definition_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


