# TheBrain MCP & API Server - 使用指南

## 🔐 安全认证

**重要**：所有 `/api/*` 接口都需要 Bearer Token 认证！

### 认证方式

使用您的 `THEBRAIN_API_KEY` 作为 Bearer Token：

```bash
# ❌ 未认证 - 返回 401
curl http://localhost:8000/api/pins

# ✅ 已认证 - 返回数据
curl -H "Authorization: Bearer YOUR_THEBRAIN_API_KEY" \
  http://localhost:8000/api/pins
```

> 💡 **提示**: 同一个 `THEBRAIN_API_KEY` 既用于访问 TheBrain 官方 API，也用于保护本服务的 RESTful API

---

## 1. 运行服务器

### 使用 Docker (推荐)

```bash
# 1. 设置环境变量
cp .env.example .env
# 编辑 .env 填入您的 API Key 和 Brain ID

# 2. 启动服务
docker-compose up -d
```

### 本地开发

```bash
conda activate thebrain-mcp
python api_server.py
```

---

## 2. 访问服务

- **API 文档**: http://localhost:8000/docs
- **MCP 端点**: http://localhost:8000/mcp/sse
- **健康检查**: http://localhost:8000/ (无需认证)

---

## 3. 在 AI 客户端中配置 (MCP)

### Claude Desktop

修改 `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "thebrain": {
      "url": "http://localhost:8000/mcp/sse"
    }
  }
}
```

> **注意**: MCP 端点不需要认证，仅用于本地 AI 工具集成

---

## 4. API 使用示例

### Python

```python
import requests

API_KEY = "your-thebrain-api-key"
BASE_URL = "http://localhost:8000"

headers = {"Authorization": f"Bearer {API_KEY}"}

# 搜索想法
response = requests.post(
    f"{BASE_URL}/api/search",
    headers=headers,
    json={"query": "Python", "max_results": 10}
)
print(response.json())

# 获取大脑统计
response = requests.get(f"{BASE_URL}/api/brain/stats", headers=headers)
print(response.json())
```

### JavaScript

```javascript
const API_KEY = 'your-thebrain-api-key';
const BASE_URL = 'http://localhost:8000';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

// 搜索想法
fetch(`${BASE_URL}/api/search`, {
  method: 'POST',
  headers,
  body: JSON.stringify({ query: 'Python', max_results: 10 })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 5. 常见问题

### Q: 为什么我的 API 请求返回 401?
A: 请确认：
1. 在请求 Header 中添加了 `Authorization: Bearer YOUR_API_KEY`
2. 使用的是正确的 `THEBRAIN_API_KEY`（与 .env 中一致）

### Q: MCP 端点需要认证吗？
A: 不需要。`/mcp/sse` 端点无需认证，专门用于本地 AI 工具（如 Claude Desktop）集成。

### Q: 可以修改认证方式吗？
A: 可以。如需自定义认证（如 JWT），请修改 `api_server.py` 中的 `verify_token` 函数。

---

完整接口文档请访问: http://localhost:8000/docs
