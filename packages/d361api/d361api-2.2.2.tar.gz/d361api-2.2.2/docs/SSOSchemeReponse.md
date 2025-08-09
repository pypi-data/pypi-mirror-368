# SSOSchemeReponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**schemes** | [**List[SSOSchemeDetails]**](SSOSchemeDetails.md) |  | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.sso_scheme_reponse import SSOSchemeReponse

# TODO update the JSON string below
json = "{}"
# create an instance of SSOSchemeReponse from a JSON string
sso_scheme_reponse_instance = SSOSchemeReponse.from_json(json)
# print the JSON string representation of the object
print(SSOSchemeReponse.to_json())

# convert the object into a dict
sso_scheme_reponse_dict = sso_scheme_reponse_instance.to_dict()
# create an instance of SSOSchemeReponse from a dict
sso_scheme_reponse_from_dict = SSOSchemeReponse.from_dict(sso_scheme_reponse_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


