# TheBrain MCP & API Server 使用指南

本项目已完成从 CLI 到 **MCP + API Server** 模式的重构。现在您可以同时通过 MCP 协议（用于 AI 助手）和 RESTful API（用于自定义集成）来操作 TheBrain。

## 1. 运行服务器

项目使用 Conda 环境 `thebrain-mcp` 进行隔离。

### 启动 API 服务器 (推荐)
API 服务器同时提供 HTTP 接口和 MCP SSE 支持。
```bash
conda activate thebrain-mcp
python api_server.py
```
- **REST API 文档**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **MCP SSE 端点**: `http://127.0.0.1:8000/mcp/sse`

### 启动 MCP 调试模式 (Stdio)
仅用于开发和测试 MCP 工具。
```bash
conda activate thebrain-mcp
python mcp_server.py dev
```

## 2. 在 AI 客户端中配置 (MCP)

### Claude Desktop
修改 `~/Library/Application Support/Claude/claude_desktop_config.json`:

#### 使用 HTTP (推荐)
```json
{
  "mcpServers": {
    "thebrain": {
      "url": "http://127.0.0.1:8000/mcp/sse"
    }
  }
}
```

#### 使用 Python 直接启动 (Stdio 模式)
```json
{
  "mcpServers": {
    "thebrain": {
      "command": "conda",
      "args": [
        "run",
        "-n",
        "thebrain-mcp",
        "python",
        "/absolute/path/to/mcp_server.py"
      ]
    }
  }
}
```

## 3. 使用接口 (RESTful API)

开启 `api_server.py` 后，您可以直接使用 curl 或其他工具访问：

### 搜索想法
```bash
curl http://127.0.0.1:8000/mcp/tools/search_thoughts -X POST -H "Content-Type: application/json" -d '{"arguments": {"query": "Python"}}'
```

### 获取文档
直接在浏览器访问 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 即可进行可视化交互。

## 4. 核心功能映射

| 功能 | MCP Tool 名称 | 对应 REST 接口 |
| :--- | :--- | :--- |
| 搜索 | `search_thoughts` | `/mcp/tools/search_thoughts` |
| 获取详情 | `get_thought` | `/mcp/tools/get_thought` |
| 获取关联图 | `get_graph` | `/mcp/tools/get_graph` |
| 创建想法 | `create_thought` | `/mcp/tools/create_thought` |
| 更新想法 | `update_thought` | `/mcp/tools/update_thought` |
| 笔记读写 | `operate_note` | `/mcp/tools/operate_note` |
| 资源访问 | `thought://{id}` | `/mcp/resources/thought/{id}` |
