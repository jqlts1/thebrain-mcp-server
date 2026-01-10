# TheBrain API 参考

## 基础信息

- **Base URL**: `https://api.bra.in`
- **认证**: `Authorization: Bearer YOUR_API_KEY`

## Thoughts API

### 获取想法详情
`GET /thoughts/{brainId}/{thoughtId}`

返回字段:
- `id` - 想法ID
- `name` - 名称
- `label` - 标签
- `typeId` - 类型ID
- `kind` - 类型 (1=Normal, 2=Type, 3=Event, 4=Tag, 5=System)
- `acType` - 访问类型 (0=Public, 1=Private)
- `foregroundColor` / `backgroundColor` - 颜色
- `creationDateTime` / `modificationDateTime` - 时间戳

### 获取想法图谱
`GET /thoughts/{brainId}/{thoughtId}/graph?includeSiblings=false`

返回想法及其附件、链接、关联想法的完整图谱。

### 按名称查找
`GET /thoughts/{brainId}?nameExact={name}`

### 创建想法
`POST /thoughts/{brainId}`

Body:
```json
{
  "name": "想法名称",
  "sourceThoughtId": "源想法ID（可选，不填则创建孤立想法）",
  "relation": 1,  // 1=Child, 2=Parent, 3=Jump, 4=Sibling
  "kind": 1,      // 1=Normal, 2=Type, 3=Event, 4=Tag
  "acType": 0,    // 0=Public, 1=Private
  "typeId": "类型ID（可选）",
  "label": "标签（可选）"
}
```

### 更新想法
`PATCH /thoughts/{brainId}/{thoughtId}`

使用 JSON Patch 格式:
```json
[{"op": "replace", "path": "/name", "value": "新名称"}]
```

### 删除想法
`DELETE /thoughts/{brainId}/{thoughtId}`

### 其他
- `GET /thoughts/{brainId}/types` - 获取所有类型
- `GET /thoughts/{brainId}/tags` - 获取所有标签
- `GET /thoughts/{brainId}/pinned` - 获取置顶想法
- `POST /thoughts/{brainId}/{thoughtId}/pin` - 置顶
- `DELETE /thoughts/{brainId}/{thoughtId}/pin` - 取消置顶
- `GET /thoughts/{brainId}/{thoughtId}/attachments` - 获取附件列表

---

## Links API

### 创建链接
`POST /links/{brainId}`

Body:
```json
{
  "thoughtIdA": "起始想法ID",
  "thoughtIdB": "目标想法ID",
  "relation": 1,  // 1=Child, 2=Parent, 3=Jump, 4=Sibling
  "name": "链接标签（可选）",
  "typeId": "链接类型ID（可选）",
  "color": "#FF7145（可选）",
  "thickness": 300
}
```

### 获取链接
- `GET /links/{brainId}/{linkId}` - 按ID获取
- `GET /links/{brainId}/{thoughtIdA}/{thoughtIdB}` - 获取两想法间的链接

返回字段:
- `id` - 链接ID
- `typeId` - 链接类型ID
- `color` - 颜色（如 #7F5926）
- `thickness` - 粗细
- `relation` - 关系类型
- `direction` - 方向 (1=IsDirected, 2=DirectionBA, 4=OneWay)
- `kind` - 类型 (1=Normal, 2=Type)

### 更新链接
`PATCH /links/{brainId}/{linkId}`

Content-Type: `application/json-patch+json`

可更新属性：
- `/typeId` - 链接类型ID
- `/color` - 颜色
- `/thickness` - 粗细
- `/name` - 标签名称
- `/relation` - 关系类型
- `/direction` - 方向

示例:
```json
[
  {"op": "replace", "path": "/typeId", "value": "uuid"},
  {"op": "replace", "path": "/color", "value": "#FF0000"}
]
```

### 删除链接
`DELETE /links/{brainId}/{linkId}`

---

## Search API

### 搜索
`GET /search/{brainId}?queryText={query}&maxResults=30&onlySearchThoughtNames=false`

参数:
- `queryText` - 搜索关键词
- `maxResults` - 最大返回数量（默认30）
- `onlySearchThoughtNames` - 是否只搜索想法名称

注意：新添加的内容可能需要15秒才能被索引。

---

## Attachments API

### 添加URL附件
`POST /attachments/{brainId}/{thoughtId}/url`

Body:
```json
{
  "url": "https://example.com",
  "name": "链接名称（可选）"
}
```

### 获取附件详情
`GET /attachments/{brainId}/{attachmentId}`

### 删除附件
`DELETE /attachments/{brainId}/{attachmentId}`

---

## Notes API

### 获取笔记
- `GET /notes/{brainId}/{thoughtId}` - 返回 Markdown 格式
- `GET /notes/{brainId}/{thoughtId}/html` - 返回 HTML 格式
- `GET /notes/{brainId}/{thoughtId}/text` - 返回纯文本格式

返回字段:
- `brainId` - Brain ID
- `sourceId` - 想法ID
- `sourceType` - 来源类型
- `markdown` / `html` / `text` - 笔记内容
- `modificationDateTime` - 修改时间

### 更新笔记
`POST /notes/{brainId}/{thoughtId}/update`

Body:
```json
{
  "markdown": "# 标题\n\n内容..."
}
```

### 追加笔记
`POST /notes/{brainId}/{thoughtId}/append`

Body:
```json
{
  "markdown": "\n\n## 追加内容\n..."
}
```

---

## 关系类型说明

| 值 | 类型 | 说明 |
|---|------|------|
| 1 | Child | 子想法（从A到B，B是A的子） |
| 2 | Parent | 父想法（从A到B，B是A的父） |
| 3 | Jump | 跳转链接（双向关联） |
| 4 | Sibling | 兄弟（同级关联） |

---

## 响应状态码

| 状态码 | 描述 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | API Key 无效 |
| 403 | 无权限 |
| 404 | 资源不存在 |
