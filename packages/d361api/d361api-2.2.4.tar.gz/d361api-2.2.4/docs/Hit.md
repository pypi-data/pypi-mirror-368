# Hit


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** | Article title | [optional] 
**content** | **str** | Article HTML content | [optional] 
**is_hidden** | **bool** | Indicates if the article is visible on the site | [optional] 
**tags** | **List[str]** | Custom article tags | [optional] 
**slug** | **str** | The slug of the article | [optional] 
**version** | **int** | The version number that is currently published | [optional] 
**article_id** | **str** | The ID of the article | [optional] 
**category_id** | **str** | The ID of the category | [optional] 
**is_category_hidden** | **bool** | Indicates if category is visible on the site | [optional] 
**order** | **int** | The position inside the parent category | [optional] 
**is_draft** | **bool** | Indicates if the article is marked as a draft | [optional] 
**exclude** | **bool** | Indicates if the article is excluded from search results on user website | [optional] 
**breadcrumb** | **str** | The breadcrumb of the article | [optional] 
**is_category** | **bool** | If the value is True, then the object has to considered as a category, otherwise it is an article | [optional] 
**attachment_ids** | **List[object]** | The IDs of the files attached to the article | [optional] 
**is_deleted** | **bool** | If the value is True, then it indicates that the article has been deleted | [optional] 
**is_folder_type_category** | **bool** | If the value is True, then it indicates that the category is a folder type category | [optional] 
**updated_on_timestamp** | **float** | The last updated timestamp of the article | [optional] 
**is_private** | **bool** | If the value is True, then the article can only be accessed by logged in users in the knowledge base site | [optional] 
**language_id** | **str** | The ID of the language | [optional] 
**project_id** | **str** | The ID of the project | [optional] 
**is_latest_version** | **bool** | If the value is True, then the article is the latest version | [optional] 
**contributors** | **List[str]** | The IDs of users who have contributed to the article | [optional] 
**is_shared_article** | **int** | If the value is True, then it indicates that it is a shared article | [optional] 
**lang_code** | **str** | The language code of the article or category | [optional] 
**category_unique_id** | **str** | A unique identifier for the category which is a combination of category ID and the language code | [optional] 
**unique_id** | **str** | A unique identifier for the article which is a combination of article ID and the language code | [optional] 
**deleted_by** | **str** | The ID of the user who deleted the article | [optional] 
**deleted_at** | **str** | The timestamp when the article was deleted | [optional] 
**is_git_hub_entity** | **bool** | If the value is True, then it indicates that the article is synced from GitHub | [optional] 
**original_article_id** | **str** | The original article ID. Applicable only for shared articles. | [optional] 
**object_id** | **str** | algolia search object ID | [optional] 
**snippet_result** | [**Snippetresult**](Snippetresult.md) | Markup text with occurrences highlighted. | [optional] 
**highlight_result** | [**Highlightresult**](Highlightresult.md) | Highlighted attributes | [optional] 

## Example

```python
from d361api.d361api.hit import Hit

# TODO update the JSON string below
json = "{}"
# create an instance of Hit from a JSON string
hit_instance = Hit.from_json(json)
# print the JSON string representation of the object
print(Hit.to_json())

# convert the object into a dict
hit_dict = hit_instance.to_dict()
# create an instance of Hit from a dict
hit_from_dict = Hit.from_dict(hit_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


