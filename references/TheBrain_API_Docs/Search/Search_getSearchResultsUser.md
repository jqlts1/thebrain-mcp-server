# Returns search results from all brains with user access

**接口路径:** `GET /search/accessible`

**描述:** Newly added content may take up to 15 seconds to be indexed.

## 参数列表

| 参数名 | 位置 | 描述 | 是否必填 | 类型 | 默认值 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| queryText | query | The string to search for | 是 | string | - |
| maxResults | query | The maximum amount of search results to return | 是 | integer (int32) | 30 |
| onlySearchThoughtNames | query | Whether to only search in thought names | 否 | boolean | false |

## 响应列表

| 状态码 | 描述 |
| :--- | :--- |
| 200 | Returns a list of search results |
| 400 | If the search failed |
| 401 | If the API Key is missing or invalid |
