# BulkArticleResultCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**article_id** | **str** | Article ID that has updated | [optional] 
**success** | **bool** | Indicates if articles creation was successful | [optional] 
**details** | **str** | Additional information about articles creation status | [optional] 

## Example

```python
from d361api.d361api.bulk_article_result_customer import BulkArticleResultCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of BulkArticleResultCustomer from a JSON string
bulk_article_result_customer_instance = BulkArticleResultCustomer.from_json(json)
# print the JSON string representation of the object
print(BulkArticleResultCustomer.to_json())

# convert the object into a dict
bulk_article_result_customer_dict = bulk_article_result_customer_instance.to_dict()
# create an instance of BulkArticleResultCustomer from a dict
bulk_article_result_customer_from_dict = BulkArticleResultCustomer.from_dict(bulk_article_result_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


