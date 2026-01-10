# TheBrain MCP & API Server - Docker 部署指南

## 快速启动

### 方法 1: 使用 Docker Compose (推荐)

1. **设置环境变量**
   ```bash
   # 创建 .env 文件
   cp .env.example .env
   # 编辑 .env 填入您的 API Key 和 Brain ID
   ```

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

3. **查看日志**
   ```bash
   docker-compose logs -f
   ```

### 方法 2: 直接使用 Docker

```bash
# 构建镜像
docker build -t thebrain-mcp:latest .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e THEBRAIN_API_KEY="your-api-key" \
  -e THEBRAIN_BRAIN_ID="your-brain-id" \
  --name thebrain-mcp \
  thebrain-mcp:latest
```

## 访问服务

- **API 文档**: http://localhost:8000/docs
- **MCP 端点**: http://localhost:8000/mcp/sse

## 管理命令

```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看容器状态
docker-compose ps

# 进入容器
docker-compose exec thebrain-api sh
```

## 注意事项

- 已锁定 `fastmcp<3` 避免破坏性更新
- 环境变量可通过 `.env` 文件或 `-e` 参数传入
- 默认端口为 8000，可在 docker-compose.yml 中修改
