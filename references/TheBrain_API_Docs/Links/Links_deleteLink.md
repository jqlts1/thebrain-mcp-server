# Deletes a link (deleteLink)

**接口路径:** `DELETE /links/{brainId}/{linkId}`

## 描述
Deletes a link

## 参数列表
| 名称 | 位置 | 描述 | 是否必填 | 类型 |
| --- | --- | --- | --- | --- |
| brainId | path | The ID of the brain | 是 | string (uuid) |
| linkId | path | The ID of the link | 是 | string (uuid) |

## 响应列表
| 状态码 | 描述 |
| --- | --- |
| 200 | Success |
| 400 | If the link can't be deleted |
| 401 | If the API Key is missing or invalid |
