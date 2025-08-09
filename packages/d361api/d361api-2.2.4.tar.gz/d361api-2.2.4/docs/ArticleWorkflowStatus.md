# ArticleWorkflowStatus


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status_id** | **str** | ID of the workflow status to apply to the listed articles. If omitted, no status change is applied. The value should match one of the predefined workflow statuses in the project. | [optional] 
**due_date** | **datetime** | Due date associated with the workflow status for completing the task or review. It should be in ISO 8601 format (yyyy-mm-ddThh:mm:ss) | [optional] 
**comment** | **str** | Optional text comment added along with the workflow status update. Useful for provided high-level instructions, context, or decisions. | [optional] 
**assignee_id** | **str** | ID of the user assigned to this workflow status. Assigning someone to a workflow status ensures they are notified via email. | [optional] 

## Example

```python
from d361api.d361api.article_workflow_status import ArticleWorkflowStatus

# TODO update the JSON string below
json = "{}"
# create an instance of ArticleWorkflowStatus from a JSON string
article_workflow_status_instance = ArticleWorkflowStatus.from_json(json)
# print the JSON string representation of the object
print(ArticleWorkflowStatus.to_json())

# convert the object into a dict
article_workflow_status_dict = article_workflow_status_instance.to_dict()
# create an instance of ArticleWorkflowStatus from a dict
article_workflow_status_from_dict = ArticleWorkflowStatus.from_dict(article_workflow_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


