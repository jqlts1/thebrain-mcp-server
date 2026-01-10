# Gets a list of all Types in a specified brain

**接口路径:** `GET /thoughts/{brainId}/types`

**描述:** Gets a list of all Types in a specified brain

## 参数列表

| 参数名 | 位置 | 描述 | 是否必填 | 类型 |
| :--- | :--- | :--- | :--- | :--- |
| brainId | path | The ID of the brain | 是 | string (uuid) |

## 响应列表

| 状态码 | 描述 |
| :--- | :--- |
| 200 | Success |
| 400 | If the list of Types failed to be retrieved |
| 401 | If the API Key is missing or invalid |
