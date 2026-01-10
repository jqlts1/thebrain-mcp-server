# Returns details about the brain accessors for the specified brain

**接口路径**: `/brain-access/{brainId}`
**方法**: `GET`

## 描述
Brain Accessor properties and values:
            
    Guid 'accessorId' - The ID of the user

    string 'name' - The name of the user

    bool 'isOrganizationUser' - If the user is part of your TeamBrain organization
    bool 'isPending' - If the brain access invitation has been sent but has not yet been accepted
            
    int 'accessType' - The user's access level for the brain
        None = 0
        Reader = 1
        Writer = 2
        Admin = 3
        PublicReader = 4

## 参数
| 名称 | 位置 | 描述 | 必填 | 类型 |
| --- | --- | --- | --- | --- |
| brainId | path | The ID of the brain | Yes | string (uuid) |

## 响应
| 状态码 | 描述 |
| --- | --- |
| 200 | Returns details about the brain accessors |
| 400 | If the brain accessors failed to be retrieved |
| 401 | If the API Key is missing or invalid |
| 403 | If the user does not have admin access |
