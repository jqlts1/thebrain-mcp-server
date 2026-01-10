# Returns the first thought matching the name exactly

**接口路径:** `GET /thoughts/{brainId}`

**描述:** Returns the first thought matching the name exactly

## 参数列表

| 参数名 | 位置 | 描述 | 是否必填 | 类型 |
| :--- | :--- | :--- | :--- | :--- |
| brainId | path | The ID of the brain | 是 | string (uuid) |
| nameExact | query | The exact name of the thought | 是 | string |

## 响应列表

| 状态码 | 描述 |
| :--- | :--- |
| 200 | Returns the first thought matching the name exactly. |
| 401 | If the API Key is missing or invalid |
