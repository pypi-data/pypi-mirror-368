# DriveTaskStatus


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**task_id** | **str** | The task ID of the file deleted | [optional] 
**is_complete** | **bool** | Indicates whether the task associated with the file deletion is complete | [optional] 
**status** | [**BackgroundTaskStatus**](BackgroundTaskStatus.md) | 0 - Queued, 1 - Initiated, 2 - InProgress, 3 - Completed, 4 - Error, 5 - Cancelled | [optional] 

## Example

```python
from d361api.d361api.drive_task_status import DriveTaskStatus

# TODO update the JSON string below
json = "{}"
# create an instance of DriveTaskStatus from a JSON string
drive_task_status_instance = DriveTaskStatus.from_json(json)
# print the JSON string representation of the object
print(DriveTaskStatus.to_json())

# convert the object into a dict
drive_task_status_dict = drive_task_status_instance.to_dict()
# create an instance of DriveTaskStatus from a dict
drive_task_status_from_dict = DriveTaskStatus.from_dict(drive_task_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


