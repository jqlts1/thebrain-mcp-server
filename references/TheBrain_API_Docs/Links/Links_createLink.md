# Creates a link (createLink)

**接口路径:** `POST /links/{brainId}`

## 描述
Link properties and expected values:
            
    Guid 'thoughtIdA' - The ID of the thought to begin the link from
    Guid 'thoughtIdB' - The ID of the thought to terminate the link at
            
    string 'name' (Optional) - The label for the link
            
    int 'relation' - The relationship of the link, relative from 'thoughtIdA' to 'thoughtIdB'
         Child = 1
         Parent = 2
         Jump = 3
         Sibling = 4

## 参数列表
| 名称 | 位置 | 描述 | 是否必填 | 类型 |
| --- | --- | --- | --- | --- |
| brainId | path | The ID of the brain | 是 | string (uuid) |

## 响应列表
| 状态码 | 描述 |
| --- | --- |
| 200 | Success - returns the newly created link ID |
| 400 | If the link can't be created |
| 401 | If the API Key is missing or invalid |
| 404 | If the source or target thought isn't found |
