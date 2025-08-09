# ArticleUpdateWorkflowRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_version_id** | **str** | Identifier of the specific workspace in the project in which the articles exist. This ID is used to ensure the workflow status update is applied to articles in a particular workspace. | 
**lang_code** | **str** | Language code of the articles whose workflow status is being updated (e.g., \&quot;en\&quot;, \&quot;fr\&quot;). This ensures the workflow status update is applied to the article in the specified language. | 
**user_id** | **str** | User ID of the team account changing the workflow status. This team account will be recorded in the audit log. | 
**article_ids** | **List[str]** | List of article IDs to be updated. Each ID in this array should refer to an existing article in the specified project version and language. | 
**workflow_status_info** | [**ArticleWorkflowStatus**](ArticleWorkflowStatus.md) | Object for workflow status metadata. This object defines the new workflow status and any associated information like due date, comment, or assignee. | 

## Example

```python
from d361api.d361api.article_update_workflow_request import ArticleUpdateWorkflowRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ArticleUpdateWorkflowRequest from a JSON string
article_update_workflow_request_instance = ArticleUpdateWorkflowRequest.from_json(json)
# print the JSON string representation of the object
print(ArticleUpdateWorkflowRequest.to_json())

# convert the object into a dict
article_update_workflow_request_dict = article_update_workflow_request_instance.to_dict()
# create an instance of ArticleUpdateWorkflowRequest from a dict
article_update_workflow_request_from_dict = ArticleUpdateWorkflowRequest.from_dict(article_update_workflow_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


