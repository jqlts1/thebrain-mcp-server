# Returns a list of brains for the active user

**接口路径**: `/brains`
**方法**: `GET`

## 描述
No description provided.

## 参数
无参数。

## 响应
| 状态码 | 描述 |
| --- | --- |
| 200 | Returns a list of brains for the user. Includes brains the user explicitly has access to or has favorited |
| 401 | If the API Key is missing or invalid |
