# GetDriveFilesInArticleDataCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**article_id** | **str** | Id of the Article | [optional] 
**file_urls** | **List[str]** | List of media files in the article | [optional] 
**extension_data** | **object** | Extention data for customer API response | [optional] 
**success** | **bool** | Status indication for customer API response | [optional] 
**errors** | [**List[BaseError]**](BaseError.md) | Errors in the customer API response | [optional] 
**warnings** | [**List[BaseWarning]**](BaseWarning.md) | Warnings in the customer API response | [optional] 
**information** | [**List[BaseInformation]**](BaseInformation.md) | Information passed by the customer API response | [optional] 

## Example

```python
from d361api.d361api.get_drive_files_in_article_data_customer import GetDriveFilesInArticleDataCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of GetDriveFilesInArticleDataCustomer from a JSON string
get_drive_files_in_article_data_customer_instance = GetDriveFilesInArticleDataCustomer.from_json(json)
# print the JSON string representation of the object
print(GetDriveFilesInArticleDataCustomer.to_json())

# convert the object into a dict
get_drive_files_in_article_data_customer_dict = get_drive_files_in_article_data_customer_instance.to_dict()
# create an instance of GetDriveFilesInArticleDataCustomer from a dict
get_drive_files_in_article_data_customer_from_dict = GetDriveFilesInArticleDataCustomer.from_dict(get_drive_files_in_article_data_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


