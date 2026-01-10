# Updates a thought using JSON Patch

**接口路径:** `PATCH /thoughts/{brainId}/{thoughtId}`

**描述:** 
Thought properties and expected values:
- Guid 'typeId' (Optional) - The ID of the thought type
- string 'name' - The Name of the thought
- string 'label' (Optional) - The Label of the thought
- string 'foregroundColor' (Optional) - The RGB hexadecimal color of the thought's foreground color (Ex: '#ff7145')
- string 'backgroundColor' (Optional) - The RGB hexadecimal color of the thought's background color (Ex: '#ff7145')
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
| thoughtId | path | The ID of the thought to be updated | 是 | string (uuid) |

## 响应列表

| 状态码 | 描述 |
| :--- | :--- |
| 200 | Success |
| 401 | If the API Key is missing or invalid |
