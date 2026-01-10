# Gets the link between two thoughts (getLink)

**接口路径:** `GET /links/{brainId}/{thoughtIdA}/{thoughtIdB}`

## 描述
Link properties and values:
            
    Guid 'id' - The ID of the link
    Guid 'brainId' - The ID of the brain containing the link
    Guid 'thoughtIdA' - The ID of the thought to begin the link from
    Guid 'thoughtIdB' - The ID of the thought to terminate the link at
    Guid 'typeId' - The ID of the link type
            
    DateTime 'creationDateTime' - The DateTime that the link was created at
    DateTime 'modificationDateTime' - The DateTime that the link was last modified at

    string 'name' - The label for the link
    string 'color' - The RGB hexadecimal color of the link (Ex: '#ff7145')
            
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

    int 'meaning' - The meaning of the link
         Normal = 1
         InstanceOf = 2   // Type (A) to Normal Thought (B)
         TypeOf = 3       // Super Type (A) to Type (B)
         HasEvent = 4
         HasTag = 5       // Tag (A) to Normal or Type Thought (B)
         System = 6
         SubTagOf = 7     // Super Tag (A) to Tag (B)

## 参数列表
| 名称 | 位置 | 描述 | 是否必填 | 类型 |
| --- | --- | --- | --- | --- |
| brainId | path | The ID of the brain | 是 | string (uuid) |
| thoughtIdA | path | The ID of the Thought A | 是 | string (uuid) |
| thoughtIdB | path | The ID of the Thought B | 是 | string (uuid) |

## 响应列表
| 状态码 | 描述 |
| --- | --- |
| 200 | Returns details about the link. |
| 401 | If the API Key is missing or invalid |
| 404 | If the link cannot be located |
