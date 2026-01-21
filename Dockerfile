# ========== Multi-stage Dockerfile ==========
# Stage 1: 构建前端 (Next.js)
FROM node:20-alpine AS frontend-builder

WORKDIR /app/web-app

# 复制前端依赖文件
COPY web-app/package*.json ./

# 安装依赖
RUN npm ci

# 复制前端源码
COPY web-app/ ./

# 构建静态文件
RUN npm run build


# Stage 2: Python 运行时
FROM python:3.10-slim

WORKDIR /app

# 复制 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY scripts/ ./scripts/
# 确保 srs 目录完整复制（包括 __init__.py）
RUN mkdir -p ./srs
COPY srs/ ./srs/
COPY mcp_server.py .
COPY api_server.py .

# 从 Stage 1 复制前端构建产物
COPY --from=frontend-builder /app/web-app/dist ./web-app/dist

# 暴露端口
EXPOSE 8000

# 环境变量 (运行时通过 -e 或 docker-compose 传入)
ENV PYTHONPATH="/app"
ENV THEBRAIN_API_KEY=""
ENV THEBRAIN_BRAIN_ID=""

# 启动服务
CMD ["python", "api_server.py"]
