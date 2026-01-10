# Updates a link using JSON Patch (updateLink)

**接口路径:** `PATCH /links/{brainId}/{linkId}`

## 描述
Link properties and expected values:
            
    Guid 'thoughtIdA' - The ID of the thought to begin the link from
    Guid 'thoughtIdB' - The ID of the thought to terminate the link at
    Guid 'typeId' (Optional) - The ID of the link type
            
    string 'name' (Optional) - The label for the link
    string 'color' (Optional) - The RGB hexadecimal color of the link (Ex: '#ff7145')
            
    int 'thickness' - The thickness of the link
            
    int 'kind' - The kind of link
         Normal = 1
         Type = 2
            
    int 'relation' - The relationship of the link, relative from 'thoughtIdA' to 'thoughtIdB'
         Child = 1
         Parent = 2
         Jump = 3
         Sibling = 4
            
    int 'direction' - The direction of the link
         IsDirected = 1   // xxx1, 1 means Is-Directed; xxx0 means Not-Directed
         DirectionBA = 2  // xx1x, 0 means A -> B, 1 means B->A, isBackward
         OneWay = 4       // x1xx, 1 means One-Way Link;

## 参数列表
| 名称 | 位置 | 描述 | 是否必填 | 类型 |
| --- | --- | --- | --- | --- |
| brainId | path | The ID of the brain | 是 | string (uuid) |
| linkId | path | The ID of the linkId to be updated | 是 | string (uuid) |

## 响应列表
| 状态码 | 描述 |
| --- | --- |
| 200 | Success |
| 401 | If the API Key is missing or invalid |
