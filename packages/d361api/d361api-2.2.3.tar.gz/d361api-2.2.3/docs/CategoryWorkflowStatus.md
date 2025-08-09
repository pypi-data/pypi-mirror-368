# CategoryWorkflowStatus


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status_id** | **str** | ID of the workflow status to apply to the listed articles. If omitted, no status change is applied. The value should match one of the predefined workflow statuses in the project. | [optional] 
**due_date** | **datetime** | Due date associated with the workflow status for completing the task or review. It should be in ISO 8601 format (yyyy-mm-ddThh:mm:ss) | [optional] 
**comment** | **str** | Optional text comment added along with the workflow status update. Useful for provided high-level instructions, context, or decisions. | [optional] 
**assignee_id** | **str** | ID of the user assigned to this workflow status. Assigning someone to a workflow status ensures they are notified via email. | [optional] 

## Example

```python
from d361api.d361api.category_workflow_status import CategoryWorkflowStatus

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryWorkflowStatus from a JSON string
category_workflow_status_instance = CategoryWorkflowStatus.from_json(json)
# print the JSON string representation of the object
print(CategoryWorkflowStatus.to_json())

# convert the object into a dict
category_workflow_status_dict = category_workflow_status_instance.to_dict()
# create an instance of CategoryWorkflowStatus from a dict
category_workflow_status_from_dict = CategoryWorkflowStatus.from_dict(category_workflow_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


