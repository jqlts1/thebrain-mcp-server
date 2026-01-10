# Deletes a brain

**接口路径**: `/brains/{id}`
**方法**: `DELETE`

## 描述
No description provided.

## 参数
| 名称 | 位置 | 描述 | 必填 | 类型 |
| --- | --- | --- | --- | --- |
| id | path | The ID of the brain | Yes | string (uuid) |

## 响应
| 状态码 | 描述 |
| --- | --- |
| 200 | Success |
| 400 | If the brain failed to be deleted |
| 401 | If the API Key is missing or invalid |
| 403 | If the user does not have access to delete the brain |
