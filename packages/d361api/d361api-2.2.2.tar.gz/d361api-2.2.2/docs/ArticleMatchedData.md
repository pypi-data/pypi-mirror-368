# ArticleMatchedData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**hits** | [**List[Hit]**](Hit.md) | The list of articles that matched the search query. | [optional] 
**nb_hits** | **int** | The number of hits (articles) matched by the query. | [optional] 
**page** | **int** | The position of the current page (zero-based). | [optional] 
**nb_pages** | **int** | The number of returned pages. Calculation is based on the total number of hits (nbHits) divided by the number of hits per page (hitsPerPage), rounded up to the nearest integer. | [optional] 
**hits_per_page** | **int** | Maximum number of hits (articles) per page. | [optional] 
**processing_time_ms** | **int** | The time the server took to process the request, in milliseconds. This doesn’t include network time. | [optional] 
**query** | **str** | The query used to search the articles. | [optional] 

## Example

```python
from d361api.d361api.article_matched_data import ArticleMatchedData

# TODO update the JSON string below
json = "{}"
# create an instance of ArticleMatchedData from a JSON string
article_matched_data_instance = ArticleMatchedData.from_json(json)
# print the JSON string representation of the object
print(ArticleMatchedData.to_json())

# convert the object into a dict
article_matched_data_dict = article_matched_data_instance.to_dict()
# create an instance of ArticleMatchedData from a dict
article_matched_data_from_dict = ArticleMatchedData.from_dict(article_matched_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


