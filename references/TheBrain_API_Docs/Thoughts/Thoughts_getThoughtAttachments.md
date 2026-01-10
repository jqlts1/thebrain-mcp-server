# Returns a list of attachments for the thought

**接口路径:** `GET /thoughts/{brainId}/{thoughtId}/attachments`

**描述:** Returns a list of attachments for the thought

## 参数列表

| 参数名 | 位置 | 描述 | 是否必填 | 类型 |
| :--- | :--- | :--- | :--- | :--- |
| brainId | path | The ID of the brain | 是 | string (uuid) |
| thoughtId | path | The ID of the thought | 是 | string (uuid) |

## 响应列表

| 状态码 | 描述 |
| :--- | :--- |
| 200 | Returns a list of attachments for the thought. |
| 401 | If the API Key is missing or invalid |
