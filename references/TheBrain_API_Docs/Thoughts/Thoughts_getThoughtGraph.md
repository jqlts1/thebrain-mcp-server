# Returns the thought and its attachments, links, and related thoughts

**接口路径:** `GET /thoughts/{brainId}/{thoughtId}/graph`

**描述:** Returns the thought and its attachments, links, and related thoughts

## 参数列表

| 参数名 | 位置 | 描述 | 是否必填 | 类型 | 默认值 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| brainId | path | The ID of the brain | 是 | string (uuid) | - |
| thoughtId | path | The ID of the thought | 是 | string (uuid) | - |
| includeSiblings | query | Whether sibling thoughts are included | 否 | boolean | false |

## 响应列表

| 状态码 | 描述 |
| :--- | :--- |
| 200 | Returns the thought and its attachments, links, and related thoughts. |
| 401 | If the API Key is missing or invalid |
