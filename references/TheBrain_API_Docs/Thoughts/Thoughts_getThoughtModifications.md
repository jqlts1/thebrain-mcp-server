# Gets a list of modification logs for the specified thought

**接口路径:** `GET /thoughts/{brainId}/{thoughtId}/modifications`

**描述:** 
`modType` values and their corresponding actions:
- **Generic Actions:** 101: Created, 102: Deleted, 103: Changed Name, etc.
- **Thoughts and Links:** 201: Changed Color, 202: Changed Label, etc.
- **Thought Specific:** 301: Forgot, 302: Remembered, etc.
- **Note Specific:** 801: Created Note, 802: Deleted Note, etc.

## 参数列表

| 参数名 | 位置 | 描述 | 是否必填 | 类型 | 默认值 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| brainId | path | The ID of the brain | 是 | string (uuid) | - |
| thoughtId | path | The ID of the thought | 是 | string (uuid) | - |
| maxLogs | query | The maximum number of modifications to return | 是 | integer (int32) | 100 |
| includeRelatedLogs | query | Whether to include related link modifications | 是 | boolean | true |

## 响应列表

| 状态码 | 描述 |
| :--- | :--- |
| 200 | Success |
| 400 | If the modification logs failed to be retrieved |
| 401 | If the API Key is missing or invalid |
