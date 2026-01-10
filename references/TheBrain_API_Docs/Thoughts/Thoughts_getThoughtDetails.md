# Returns details about the thought

**接口路径:** `GET /thoughts/{brainId}/{thoughtId}`

**描述:** 
Thought properties and values:
- Guid 'id' - The ID of the thought
- Guid 'brainId' - The ID of the brain containing the thought
- Guid 'typeId' - The ID of the thought type
- DateTime 'creationDateTime' - The DateTime that the thought was created at
- DateTime 'modificationDateTime' - The DateTime that the thought was last modified at
- DateTime 'forgottenDateTime' - The DateTime that the thought was forgotten at
- DateTime 'linksModificationDateTime' - The DateTime that the thought's links were last modified at
- string 'name' - The Name of the thought
- string 'label' - The Label of the thought
- string 'foregroundColor' - The RGB hexadecimal color of the thought's foreground color (Ex: '#ff7145')
- string 'backgroundColor' - The RGB hexadecimal color of the thought's background color (Ex: '#ff7145')
- int 'acType' - The access type of the thought
    - Public = 0
    - Private = 1
- int 'kind' - The kind of thought
    - Normal = 1
    - Type = 2
    - Event = 3
    - Tag = 4
    - System = 5

## 参数列表

| 参数名 | 位置 | 描述 | 是否必填 | 类型 |
| :--- | :--- | :--- | :--- | :--- |
| brainId | path | The ID of the brain | 是 | string (uuid) |
| thoughtId | path | The ID of the thought | 是 | string (uuid) |

## 响应列表

| 状态码 | 描述 |
| :--- | :--- |
| 200 | Returns details about the thought. |
| 401 | If the API Key is missing or invalid |
