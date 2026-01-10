# Removes a user's access to the specified brain

**接口路径**: `/brain-access/{brainId}`
**方法**: `DELETE`

## 描述
Provide either an `emailAddress` or `userId` value, but not both.
            
`emailAddress` can be used if the `userId` is unknown.

## 参数
| 名称 | 位置 | 描述 | 必填 | 类型 |
| --- | --- | --- | --- | --- |
| brainId | path | The ID of the brain | Yes | string (uuid) |
| emailAddress | query | The email address of the user | No | string |
| userId | query | The ID of the user | No | string (uuid) |

## 响应
| 状态码 | 描述 |
| --- | --- |
| 200 | Success |
| 400 | If the user's access failed to be removed |
| 401 | If the API Key is missing or invalid |
| 403 | If the user does not have admin access |
