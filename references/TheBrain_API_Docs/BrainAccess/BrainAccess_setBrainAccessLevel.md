# Sets the brain access level for the specified user

**接口路径**: `/brain-access/{brainId}`
**方法**: `POST`

## 描述
Provide either an `emailAddress` or `userId` value, but not both.
            
`emailAddress` can be used if the `userId` is unknown, or if adding someone who is not already a brain accessor
            
<hr />

Expected `accessType` values:
            
    int 'accessType' - The user's access level for the brain
        Reader = 1
        Writer = 2
        Admin = 3
        PublicReader = 4

## 参数
| 名称 | 位置 | 描述 | 必填 | 类型 |
| --- | --- | --- | --- | --- |
| brainId | path | The ID of the brain | Yes | string (uuid) |
| emailAddress | query | The email address of the user | No | string |
| userId | query | The ID of the user | No | string (uuid) |
| accessType | query | The access level to give to the user | Yes | integer (int32) |

## 响应
| 状态码 | 描述 |
| --- | --- |
| 200 | Success |
| 400 | If the brain access level failed to be changed for the user |
| 401 | If the API Key is missing or invalid |
| 403 | If the user does not have admin access |
