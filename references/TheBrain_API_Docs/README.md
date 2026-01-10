# TheBrain API 文档索引

## 📁 接口分类

### Baseurl

BaseUrl: https://api.bra.in
Token:3f4c6617b0a49ea5ba1175362eb2c0994c1152574312c8b4a197e7357eb7d187
BrainId:624c0c12-e2ef-4600-b595-c9af27967e7b

### 🧠 [Brains](./Brains)

大脑管理相关接口，用于获取、创建和删除大脑。

| 接口 | 方法 | 描述 | 主要参数 |
| :--- | :--- | :--- | :--- |
| [获取大脑列表](./Brains/Brains_getBrains.md) | GET | 返回当前用户的所有大脑列表 | 无 |
| [创建大脑](./Brains/Brains_createBrain.md) | POST | 创建一个新的 Brain | 无 |
| [获取大脑详情](./Brains/Brains_getBrainDetails.md) | GET | 返回指定大脑的详细信息 | `id` (path) - 大脑ID |
| [获取大脑统计](./Brains/Brains_getBrainStats.md) | GET | 获取大脑的统计信息（想法数、链接数、附件大小等） | `brainId` (path) - 大脑ID |
| [获取修改日志](./Brains/Brains_getBrainModifications.md) | GET | 获取大脑的修改记录，支持按时间范围筛选 | `brainId` (path), `maxLogs`, `startTime`, `endTime` |
| [删除大脑](./Brains/Brains_deleteBrain.md) | DELETE | 删除指定的大脑 | `id` (path) - 大脑ID |

---

### 💡 [Thoughts](./Thoughts)

想法（Thought）管理接口，TheBrain 的核心数据单元。

| 接口 | 方法 | 描述 | 主要参数 |
| :--- | :--- | :--- | :--- |
| [根据名称获取想法](./Thoughts/Thoughts_getThoughtByName.md) | GET | 根据精确名称查找想法 | `brainId` (path), `nameExact` (query) |
| [创建想法](./Thoughts/Thoughts_createThought.md) | POST | 创建新的想法，可指定类型、关系等 | `brainId` (path) - body 包含 name, typeId, kind, relation 等 |
| [获取想法详情](./Thoughts/Thoughts_getThoughtDetails.md) | GET | 获取想法的完整信息 | `brainId` (path), `thoughtId` (path) |
| [更新想法](./Thoughts/Thoughts_updateThought.md) | PATCH | 使用 JSON Patch 更新想法属性 | `brainId` (path), `thoughtId` (path) |
| [删除想法](./Thoughts/Thoughts_deleteThought.md) | DELETE | 删除指定的想法 | `brainId` (path), `thoughtId` (path) |
| [获取标签列表](./Thoughts/Thoughts_getTags.md) | GET | 获取大脑中所有标签 | `brainId` (path) |
| [获取类型列表](./Thoughts/Thoughts_getTypes.md) | GET | 获取大脑中所有想法类型 | `brainId` (path) |
| [获取置顶想法](./Thoughts/Thoughts_getPinnedThoughts.md) | GET | 获取大脑中所有置顶的想法 | `brainId` (path) |
| [获取想法修改日志](./Thoughts/Thoughts_getThoughtModifications.md) | GET | 获取想法的修改历史记录 | `brainId` (path), `thoughtId` (path), `maxLogs`, `includeRelatedLogs` |
| [获取想法图谱](./Thoughts/Thoughts_getThoughtGraph.md) | GET | 获取想法及其附件、链接、关联想法的完整图谱 | `brainId` (path), `thoughtId` (path), `includeSiblings` |
| [置顶想法](./Thoughts/Thoughts_pinThought.md) | POST | 将想法设为置顶 | `brainId` (path), `thoughtId` (path) |
| [取消置顶](./Thoughts/Thoughts_unpinThought.md) | DELETE | 取消想法的置顶状态 | `brainId` (path), `thoughtId` (path) |
| [获取想法附件列表](./Thoughts/Thoughts_getThoughtAttachments.md) | GET | 获取想法的所有附件 | `brainId` (path), `thoughtId` (path) |

---

### 🔗 [Links](./Links)

链接（Link）管理接口，连接想法之间的关系。

| 接口 | 方法 | 描述 | 主要参数 |
| :--- | :--- | :--- | :--- |
| [创建链接](./Links/Links_createLink.md) | POST | 在两个想法之间创建链接 | `brainId` (path) - body 包含 thoughtIdA, thoughtIdB, relation 等 |
| [获取链接详情](./Links/Links_getLinkDetails.md) | GET | 获取链接的完整信息 | `brainId` (path), `linkId` (path) |
| [更新链接](./Links/Links_updateLink.md) | PATCH | 使用 JSON Patch 更新链接属性 | `brainId` (path), `linkId` (path) |
| [删除链接](./Links/Links_deleteLink.md) | DELETE | 删除指定的链接 | `brainId` (path), `linkId` (path) |
| [获取两想法间的链接](./Links/Links_getLink.md) | GET | 获取两个指定想法之间的链接 | `brainId` (path), `thoughtIdA` (path), `thoughtIdB` (path) |
| [获取链接附件列表](./Links/Links_getLinkAttachments.md) | GET | 获取链接的所有附件 | `brainId` (path), `linkId` (path) |

---

### 📎 [Attachments](./Attachments)

附件管理接口，为想法添加文件和 URL 附件。

| 接口 | 方法 | 描述 | 主要参数 |
| :--- | :--- | :--- | :--- |
| [添加文件附件](./Attachments/Attachments_addAttachment.md) | POST | 为想法添加文件附件 | `brainId` (path), `thoughtId` (path) |
| [添加 URL 附件](./Attachments/Attachments_addUrlAttachment.md) | POST | 为想法添加 URL 链接附件 | `brainId` (path), `thoughtId` (path), `url`, `name` |
| [获取附件内容](./Attachments/Attachments_getAttachmentContent.md) | GET | 获取附件的二进制数据 | `brainId` (path), `attachmentId` (path) |
| [获取附件详情](./Attachments/Attachments_getAttachmentDetails.md) | GET | 获取附件的元数据信息 | `brainId` (path), `attachmentId` (path) |
| [删除附件](./Attachments/Attachments_deleteAttachment.md) | DELETE | 删除指定的附件 | `brainId` (path), `attachmentId` (path) |

---

### 🔍 [Search](./Search)

搜索接口，支持多种搜索范围。

| 接口 | 方法 | 描述 | 主要参数 |
| :--- | :--- | :--- | :--- |
| [搜索结果](./Search/Search_getSearchResults.md) | GET | 在指定大脑中搜索内容 | `brainId` (path), `queryText`, `maxResults`, `onlySearchThoughtNames` |
| [用户搜索](./Search/Search_getSearchResultsUser.md) | GET | 在用户有权访问的所有大脑中搜索 | `queryText`, `maxResults`, `onlySearchThoughtNames` |
| [公共搜索](./Search/Search_getSearchResultsPublic.md) | GET | 在所有公共大脑中搜索 | `queryText`, `maxResults`, `onlySearchThoughtNames`, `excludeBrainIds` |

---

### 👤 [Users & Access](./Users)

用户和访问权限管理接口。

| 接口 | 方法 | 描述 | 主要参数 |
| :--- | :--- | :--- | :--- |
| [获取组织成员](./Users/Users_getOrganizationMembers.md) | GET | 获取 TeamBrain 组织成员列表 | 无 |
| [获取大脑访问者](./BrainAccess/BrainAccess_getBrainAccessors.md) | GET | 获取有权限访问指定大脑的用户列表 | `brainId` (path) |
| [设置访问级别](./BrainAccess/BrainAccess_setBrainAccessLevel.md) | POST | 设置用户的访问权限级别 | `brainId` (path), `emailAddress`/`userId`, `accessType` |
| [移除访问权限](./BrainAccess/BrainAccess_removeBrainAccess.md) | DELETE | 移除用户对指定大脑的访问权限 | `brainId` (path), `emailAddress`/`userId` |

---

## 📚 通用说明

### 认证
所有接口都需要在请求头中提供有效的 API Key：
```
Authorization: Bearer YOUR_API_KEY
```

### 路径参数
- `{brainId}` - 大脑的唯一标识符 (UUID)
- `{thoughtId}` - 想法的唯一标识符 (UUID)
- `{linkId}` - 链接的唯一标识符 (UUID)
- `{attachmentId}` - 附件的唯一标识符 (UUID)

### 响应状态码
| 状态码 | 描述 |
| :--- | :--- |
| 200 | 成功 |
| 400 | 请求参数错误或操作失败 |
| 401 | API Key 缺失或无效 |
| 403 | 无权限执行此操作 |
| 404 | 资源不存在 |
