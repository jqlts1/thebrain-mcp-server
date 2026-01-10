# Returns the binary data for the attachment

**接口路径**: `/attachments/{brainId}/{attachmentId}/file-content`
**方法**: `GET`

## 描述
No description provided.

## 参数
| 名称 | 位置 | 描述 | 必填 | 类型 |
| --- | --- | --- | --- | --- |
| brainId | path | The ID of the brain | Yes | string (uuid) |
| attachmentId | path | The ID of the attachment | Yes | string (uuid) |

## 响应
| 状态码 | 描述 |
| --- | --- |
| 200 | Returns the binary data for the attachment. |
| 401 | If the API Key is missing or invalid |
