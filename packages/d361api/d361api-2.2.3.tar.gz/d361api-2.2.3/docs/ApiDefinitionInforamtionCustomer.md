# ApiDefinitionInforamtionCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**upload_type** | **str** |  | [optional] 

## Example

```python
from d361api.d361api.api_definition_inforamtion_customer import ApiDefinitionInforamtionCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of ApiDefinitionInforamtionCustomer from a JSON string
api_definition_inforamtion_customer_instance = ApiDefinitionInforamtionCustomer.from_json(json)
# print the JSON string representation of the object
print(ApiDefinitionInforamtionCustomer.to_json())

# convert the object into a dict
api_definition_inforamtion_customer_dict = api_definition_inforamtion_customer_instance.to_dict()
# create an instance of ApiDefinitionInforamtionCustomer from a dict
api_definition_inforamtion_customer_from_dict = ApiDefinitionInforamtionCustomer.from_dict(api_definition_inforamtion_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


