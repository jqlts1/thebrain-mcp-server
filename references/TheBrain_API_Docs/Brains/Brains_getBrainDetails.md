# Returns details about one of the active user's brains

**接口路径**: `/brains/{id}`
**方法**: `GET`

## 描述
No description provided.

## 参数
| 名称 | 位置 | 描述 | 必填 | 类型 |
| --- | --- | --- | --- | --- |
| id | path | The ID of the brain | Yes | string (uuid) |

## 响应
| 状态码 | 描述 |
| --- | --- |
| 200 | Returns details about the brain. |
| 401 | If the API Key is missing or invalid |
