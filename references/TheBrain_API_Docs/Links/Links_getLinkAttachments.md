# Returns a list of attachments for the link (getLinkAttachments)

**接口路径:** `GET /links/{brainId}/{linkId}/attachments`

## 描述
Returns a list of attachments for the link

## 参数列表
| 名称 | 位置 | 描述 | 是否必填 | 类型 |
| --- | --- | --- | --- | --- |
| brainId | path | The ID of the brain | 是 | string (uuid) |
| linkId | path | The ID of the link | 是 | string (uuid) |

## 响应列表
| 状态码 | 描述 |
| --- | --- |
| 200 | Returns a list of attachments for the link. |
| 401 | If the API Key is missing or invalid |
