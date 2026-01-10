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
# 编辑 .env 填入您的 API Key 和 Brain ID

# 2. 启动服务
docker-compose up -d

# 3. 访问
# API 文档: http://localhost:8000/docs
# MCP 端点: http://localhost:8000/mcp/sse
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

完整的 22 个接口包括：

| 分类 | 接口 | 说明 |
| :--- | :--- | :--- |
| **搜索** | `POST /api/search` | 搜索想法（增强字段） |
| | `POST /api/search/raw` | 原始搜索结果 |
| **想法** | `GET /api/thoughts/{id}` | 获取详情 |
| | `GET /api/thoughts/by-name` | 按名称查找 |
| | `POST /api/thoughts` | 创建想法 |
| | `PATCH /api/thoughts/{id}` | 更新想法 |
| | `POST /api/thoughts/{id}/pin` | 置顶 |
| **链接** | `GET /api/links/{id}` | 链接详情 |
| | `PATCH /api/links/{id}` | 更新链接 |
| **大脑** | `GET /api/brain/stats` | 统计信息 |
| | `GET /api/brain/modifications` | 修改日志 |

查看完整文档：[USAGE_MCP.md](USAGE_MCP.md)

## MCP 集成

### Claude Desktop

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "thebrain": {
      "url": "http://localhost:8000/mcp/sse"
    }
  }
}
```

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
THEBRAIN_API_KEY=your-api-key-here
THEBRAIN_BRAIN_ID=your-brain-id-here
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
