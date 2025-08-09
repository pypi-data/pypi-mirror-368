# WorkflowStatusCustomer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique identifier of the workflow status. This ID is used while updating the workflow status for articles and page categories using the Update workflow status of articles and Update workflow status of page categories endpoints respectively. | [optional] 
**name** | **str** | Display name of the workflow status (e.g., \&quot;Draft\&quot;, \&quot;In Review\&quot;). The workflow status is displayed to all team accounts working on the article. | [optional] 
**description** | **str** | Optional explanation of the status. Used to clarify the intent or usage of the status in the workflow. May be blank if no description was provided during setup. | [optional] 
**read_only** | **bool** | Indicates whether read-only mode is toggled on for the workflow status. &lt;br&gt;&lt;/br&gt;  • true: workflow status is set to read-only.No edits can be made to the article.No comments can be added to the article. &lt;br&gt;&lt;/br&gt;  • false: Contributors can edit the article and add comments to the article to provide feedback. | [optional] 

## Example

```python
from d361api.d361api.workflow_status_customer import WorkflowStatusCustomer

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowStatusCustomer from a JSON string
workflow_status_customer_instance = WorkflowStatusCustomer.from_json(json)
# print the JSON string representation of the object
print(WorkflowStatusCustomer.to_json())

# convert the object into a dict
workflow_status_customer_dict = workflow_status_customer_instance.to_dict()
# create an instance of WorkflowStatusCustomer from a dict
workflow_status_customer_from_dict = WorkflowStatusCustomer.from_dict(workflow_status_customer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


