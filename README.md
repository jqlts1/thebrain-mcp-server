# TheBrain MCP & API Server

将 TheBrain 知识图谱接口封装为 MCP (Model Context Protocol) 服务器和 RESTful API，支持 AI 助手集成和自定义开发。

## 特性

- 🧠 **MCP 协议支持** - 可集成到 Claude Desktop、Cursor 等 AI 工具
- 🌐 **RESTful API** - 22 个完整的 HTTP 接口
- 🔍 **增强搜索** - 丰富的返回字段，支持原始结果查询
- 📌 **置顶管理** - 想法置顶/取消置顶
- 🔗 **链接操作** - 查看和更新想法间的链接关系
- 📊 **统计信息** - 获取大脑统计数据和修改日志
- 🐳 **Docker 支持** - 一键部署

## 快速开始

### 使用 Docker (推荐)

```bash
# 1. 设置环境变量
cp .env.example .env
# 编辑 .env 填入：
# - THEBRAIN_API_KEY
# - THEBRAIN_BRAIN_ID

# 2. 启动服务
docker-compose up -d

# 3. 访问
# API 文档: http://localhost:8000/docs
# MCP 端点: http://localhost:8000/mcp/mcp
```

### 本地开发

```bash
# 1. 创建环境
conda create -n thebrain-mcp python=3.10 -y
conda activate thebrain-mcp

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env

# 4. 启动服务
python api_server.py
```

## API 接口

### 🔐 认证说明

所有 `/api/*` 接口都需要 **Bearer Token 认证**，使用您的 `THEBRAIN_API_KEY` 作为 token：

```bash
curl -H "Authorization: Bearer YOUR_THEBRAIN_API_KEY" \
  http://localhost:8000/api/pins
```

### 📋 完整接口列表

#### 搜索相关

| 接口 | 方法 | 说明 | 主要参数 |
| :--- | :--- | :--- | :--- |
| `/api/search` | POST | 搜索想法（增强字段） | `query`, `max_results` |
| `/api/search/raw` | POST | 原始搜索结果（含匹配上下文） | `query`, `max_results`, `only_names` |
| `/api/search/by-type` | POST | 按类型/标签过滤搜索 🆕 | `query`, `type_id`, `tag_id`, `max_results` |
| `/api/search/related` | POST | 多关键词相关性搜索 🆕 | `keywords` (List), `max_results` |

#### 想法操作

| 接口 | 方法 | 说明 | 主要参数 |
| :--- | :--- | :--- | :--- |
| `/api/thoughts/{id}` | GET | 获取想法详情 | `id` (路径参数) |
| `/api/thoughts/by-name` | GET | 按名称精确查找想法 | `name` (查询参数) |
| `/api/thoughts/{id}/graph` | GET | 获取想法关联图谱 | `id`, `siblings` (可选) |
| `/api/thoughts/{id}/children` | GET | 获取子想法列表 | `id` |
| `/api/thoughts/{id}/parents` | GET | 获取父想法列表 | `id` |
| `/api/thoughts/{id}/jumps` | GET | 获取跳转链接 | `id` |
| `/api/thoughts` | POST | 创建新想法 | `name`, `parent_id`/`jump_id`, `kind` |
| `/api/thoughts/{id}` | PATCH | 更新想法属性 | `id`, `name`/`label`/`color`/`type_id` |
| `/api/thoughts/{id}` | DELETE | 删除想法 | `id` |
| `/api/thoughts/{id}/pin` | POST | 置顶想法 | `id` |
| `/api/thoughts/{id}/pin` | DELETE | 取消置顶 | `id` |
| `/api/thoughts/{id}/context` | GET | 获取完整上下文 🆕 | `id` |
| `/api/thoughts/{id}/neighbors` | GET | 多层级邻居探索 🆕 | `id`, `depth`, `include_notes` |
| `/api/thoughts/recent` | GET | 获取最近修改的想法 🆕 | `days`, `max_results` |

#### 链接操作

| 接口 | 方法 | 说明 | 主要参数 |
| :--- | :--- | :--- | :--- |
| `/api/links` | POST | 创建链接 | `thought_id_a`, `thought_id_b`, `relation` |
| `/api/links/{id}` | GET | 获取链接详情 | `id` |
| `/api/links/between/{a}/{b}` | GET | 获取两想法间的链接 | `a`, `b` (想法ID) |
| `/api/links/{id}` | PATCH | 更新链接属性 | `id`, `color`/`thickness`/`name` |
| `/api/links/{id}` | DELETE | 删除链接 | `id` |

#### 笔记操作

| 接口 | 方法 | 说明 | 主要参数 |
| :--- | :--- | :--- | :--- |
| `/api/thoughts/{id}/note` | GET | 获取笔记 | `id`, `format` (markdown/html/text) |
| `/api/thoughts/{id}/note` | POST | 更新/追加笔记 | `id`, `content`, `append` |

#### 元数据

| 接口 | 方法 | 说明 | 主要参数 |
| :--- | :--- | :--- | :--- |
| `/api/types` | GET | 获取所有类型 | 无 |
| `/api/tags` | GET | 获取所有标签 | 无 |
| `/api/pins` | GET | 获取置顶想法列表 | 无 |

#### 附件操作

| 接口 | 方法 | 说明 | 主要参数 |
| :--- | :--- | :--- | :--- |
| `/api/thoughts/{id}/attachments` | GET | 获取附件列表 | `id` |
| `/api/thoughts/{id}/attachments/url` | POST | 添加 URL 附件 | `id`, `url`, `name` (可选) |

#### 大脑统计

| 接口 | 方法 | 说明 | 主要参数 |
| :--- | :--- | :--- | :--- |
| `/api/brain/stats` | GET | 获取大脑统计信息 | 无 |
| `/api/brain/modifications` | GET | 获取修改日志 | `max_logs`, `start_time`, `end_time` |

**总计**: 27 个 RESTful API 接口

查看完整文档和在线测试: http://localhost:8000/docs

## MCP 集成

### MCP 工具列表

| 工具名 | 说明 | 必需参数 | 可选参数 |
| :--- | :--- | :--- | :--- |
| `search_thoughts` | 搜索想法 | `query` | `n` (默认30) |
| `get_thought` | 获取想法详情 | `thought_id` | - |
| `get_graph` | 获取想法的关联图谱 | `thought_id` | `siblings` (默认false) |
| `create_thought` | 创建新想法 | `name` | `parent_id`, `jump_id`, `kind` |
| `update_thought` | 更新想法属性 | `thought_id` | `name`, `label`, `color`, `type_id` |
| `delete_thought` | 删除想法 | `thought_id` | - |
| `create_link` | 创建链接 | `thought_id_a`, `thought_id_b` | `relation` (默认3=跳转), `name` |
| `delete_link` | 删除链接 | `link_id` | - |
| `get_note` | 获取笔记 | `thought_id` | `format` (默认markdown) |
| `update_note` | 覆盖笔记 ⚠️ | `thought_id`, `content` | - |
| `append_note` | 追加笔记 ✅ | `thought_id`, `content` | - |
| `list_metadata` | 列出元数据 | `category` (types/tags/pins) | - |
| `import_structure` | 导入结构化数据 | `parent_id`, `data` (JSON字符串) | - |
| `search_by_type` | 按类型/标签过滤搜索 | - | `query`, `type_id`, `tag_id`, `max_results` |
| `explore_neighbors` | 多层级探索邻居节点 | `thought_id` | `depth` (1-3,默认2), `include_notes` |
| `get_context` | 获取完整上下文 | `thought_id` | - |
| `recent_thoughts` | 获取最近修改的想法 | - | `days` (默认7), `max_results` (默认20) |
| `find_related` | 按关键词查找相关想法 | `keywords` (逗号分隔) | `max_results` (默认10) |


### MCP 认证

> ⚠️ **新增**: MCP 服务器现在也支持 Bearer Token 认证，使用与 RESTful API 相同的 `THEBRAIN_API_KEY`。

### Claude Desktop

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "thebrain": {
      "url": "http://localhost:8000/mcp/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_THEBRAIN_API_KEY"
      }
    }
  }
}
```

### n8n 集成

在 n8n 中添加 MCP Client 节点，配置如下：

- **Connection Type**: Streamable HTTP
- **URL**: `http://localhost:8000/mcp/mcp`
- **Authentication**: 在 Headers 中添加 `Authorization: Bearer YOUR_THEBRAIN_API_KEY`

> **注意**: 确保所有工具参数都有明确的类型定义。如果遇到 `Cannot read properties of undefined (reading 'inputType')` 错误，请检查 MCP 服务器版本是否最新。

> **传输协议**: 使用 **HTTP Streamable** 协议（推荐），支持高效双向通信

## 技术栈

- **FastMCP** - MCP 协议实现 (锁定 <3 版本)
- **FastAPI** - RESTful API 框架
- **Requests** - TheBrain API 客户端

## 项目结构

```
.
├── scripts/
│   ├── client.py          # TheBrain API 客户端
│   └── thebrain.py        # CLI 工具
├── mcp_server.py          # MCP 服务器
├── api_server.py          # FastAPI 服务器
├── Dockerfile             # Docker 镜像
├── docker-compose.yml     # Docker Compose 配置
└── requirements.txt       # Python 依赖
```

## 环境变量

```bash
THEBRAIN_API_KEY=your-api-key-here  # 用于访问 TheBrain API 和保护本服务的 RESTful API
THEBRAIN_BRAIN_ID=your-brain-id-here
```

> ⚠️ **注意**: `THEBRAIN_API_KEY` 同时用于：
> 1. 访问 TheBrain 官方 API
> 2. 保护本服务的 RESTful API（作为 Bearer Token）

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
