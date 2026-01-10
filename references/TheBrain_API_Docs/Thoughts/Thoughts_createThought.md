# Creates a thought

**接口路径:** `POST /thoughts/{brainId}`

**描述:** 
Thought properties and expected values:
- string 'name' - The Name of the thought
- string 'label' (Optional) - The Label of the thought
- Guid 'sourceThoughtId' (Optional) - The ID of source thought. Exclude to create an Orphan thought
- Guid 'typeId' (Optional) - The ID of the thought type
- int 'acType' - The access type of the thought
    - Public = 0
    - Private = 1
- int 'kind' - The kind of thought
    - Normal = 1
    - Type = 2
    - Event = 3
    - Tag = 4
    - System = 5
- int 'relation' - The relationship of the created thought to the source thought
    - Child = 1
    - Parent = 2
    - Jump = 3
    - Sibling = 4

## 参数列表

| 参数名 | 位置 | 描述 | 是否必填 | 类型 |
| :--- | :--- | :--- | :--- | :--- |
| brainId | path | The ID of the brain | 是 | string (uuid) |

## 响应列表

| 状态码 | 描述 |
| :--- | :--- |
| 200 | Success - returns the ID of the newly created thought. |
| 400 | If the creation of the thought failed |
| 401 | If the API Key is missing or invalid |
| 404 | If the 'sourceId' thought was not found |
