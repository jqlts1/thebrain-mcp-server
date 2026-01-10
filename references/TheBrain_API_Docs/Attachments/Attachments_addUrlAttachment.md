# Adds a new URL attachment to a thought

**接口路径**: `/attachments/{brainId}/{thoughtId}/url`
**方法**: `POST`

## 描述
Leave `name` empty to automatically set it from the page's title element

## 参数
| 名称 | 位置 | 描述 | 必填 | 类型 |
| --- | --- | --- | --- | --- |
| brainId | path | The ID of the brain | Yes | string (uuid) |
| thoughtId | path | The ID of the thought to add the attachment to | Yes | string (uuid) |
| url | query | The URL for the attachment | Yes | string |
| name | query | The desired name of the URL attachment | No | string |

## 响应
| 状态码 | 描述 |
| --- | --- |
| 200 | Success |
| 400 | If the attachment could not be added to the thought. |
| 401 | If the API Key is missing or invalid |
