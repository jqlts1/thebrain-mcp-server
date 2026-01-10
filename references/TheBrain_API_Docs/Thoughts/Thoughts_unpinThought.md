# Un-pins the specified thought

**接口路径:** `DELETE /thoughts/{brainId}/{thoughtId}/pin`

**描述:** Un-pins the specified thought

## 参数列表

| 参数名 | 位置 | 描述 | 是否必填 | 类型 |
| :--- | :--- | :--- | :--- | :--- |
| brainId | path | The ID of the brain | 是 | string (uuid) |
| thoughtId | path | The ID of the thought | 是 | string (uuid) |

## 响应列表

| 状态码 | 描述 |
| :--- | :--- |
| 200 | Success |
| 400 | If the thought failed to be un-pinned |
| 401 | If the API Key is missing or invalid |
| 404 | If the provided thought was not found |
