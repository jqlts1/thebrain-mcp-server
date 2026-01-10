# Adds a new file attachment to a thought

**接口路径**: `/attachments/{brainId}/{thoughtId}/file`
**方法**: `POST`

## 描述
No description provided.

## 参数
| 名称 | 位置 | 描述 | 必填 | 类型 |
| --- | --- | --- | --- | --- |
| brainId | path | The ID of the brain | Yes | string (uuid) |
| thoughtId | path | The ID of the thought to add the attachment to | Yes | string (uuid) |

## 响应
| 状态码 | 描述 |
| --- | --- |
| 200 | Success |
| 400 | If the attachment could not be added to the thought. |
| 401 | If the API Key is missing or invalid |
