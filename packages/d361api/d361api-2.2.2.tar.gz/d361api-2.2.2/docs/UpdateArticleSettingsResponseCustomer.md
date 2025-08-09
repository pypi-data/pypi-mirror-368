# UpdateArticleSettingsResponseCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**ArticleSettingCustomerResponse**](ArticleSettingCustomerResponse.md) | update article settings | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.update_article_settings_response_customer import UpdateArticleSettingsResponseCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateArticleSettingsResponseCustomer from a JSON string
update_article_settings_response_customer_instance = UpdateArticleSettingsResponseCustomer.from_json(json)
# print the JSON string representation of the object
print(UpdateArticleSettingsResponseCustomer.to_json())

# convert the object into a dict
update_article_settings_response_customer_dict = update_article_settings_response_customer_instance.to_dict()
# create an instance of UpdateArticleSettingsResponseCustomer from a dict
update_article_settings_response_customer_from_dict = UpdateArticleSettingsResponseCustomer.from_dict(update_article_settings_response_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


