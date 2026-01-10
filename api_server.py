import sys
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 添加 scripts 目录到路径
sys.path.append(str(Path(__file__).parent / "scripts"))

from client import TheBrainClient
from mcp_server import mcp

# ========== Pydantic 模型 ==========
class SearchRequest(BaseModel):
    query: str
    max_results: int = 30

class ThoughtCreateRequest(BaseModel):
    name: str
    parent_id: Optional[str] = None
    jump_id: Optional[str] = None
    kind: int = 1  # 1=普通, 2=类型, 4=标签

class ThoughtUpdateRequest(BaseModel):
    name: Optional[str] = None
    label: Optional[str] = None
    color: Optional[str] = None
    type_id: Optional[str] = None

class LinkRequest(BaseModel):
    thought_id_a: str
    thought_id_b: str
    relation: int = 3  # 1=子, 2=父, 3=跳转
    name: Optional[str] = None

class NoteRequest(BaseModel):
    content: str
    append: bool = False

class UrlAttachmentRequest(BaseModel):
    url: str
    name: Optional[str] = None

# ========== FastAPI 应用 ==========
app = FastAPI(
    title="TheBrain API & MCP Server",
    description="TheBrain 知识图谱 RESTful API 和 MCP 服务器",
    version="1.0.0"
)

# 挂载 MCP SSE 端点
mcp_app = mcp.http_app(transport="sse")
app.mount("/mcp", mcp_app)

# 初始化客户端
def get_client():
    try:
        return TheBrainClient()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== API 路由 ==========

@app.get("/", tags=["系统"])
async def root():
    """获取服务状态"""
    return {
        "message": "TheBrain API & MCP Server is running",
        "mcp_endpoint": "/mcp/sse",
        "docs": "/docs"
    }

# ---------- 搜索 ----------
@app.post("/api/search", tags=["搜索"])
async def search_thoughts(request: SearchRequest):
    """搜索想法"""
    client = get_client()
    return client.search(request.query, request.max_results)

# ---------- 想法 CRUD ----------
@app.get("/api/thoughts/{thought_id}", tags=["想法"])
async def get_thought(thought_id: str):
    """获取想法详情"""
    client = get_client()
    return client.get_thought(thought_id)

@app.get("/api/thoughts/{thought_id}/graph", tags=["想法"])
async def get_graph(thought_id: str, siblings: bool = False):
    """获取想法的关联图谱"""
    client = get_client()
    return client.get_graph(thought_id, siblings)

@app.get("/api/thoughts/{thought_id}/children", tags=["想法"])
async def get_children(thought_id: str):
    """获取子想法"""
    client = get_client()
    return client.get_children(thought_id)

@app.get("/api/thoughts/{thought_id}/parents", tags=["想法"])
async def get_parents(thought_id: str):
    """获取父想法"""
    client = get_client()
    return client.get_parents(thought_id)

@app.get("/api/thoughts/{thought_id}/jumps", tags=["想法"])
async def get_jumps(thought_id: str):
    """获取跳转链接"""
    client = get_client()
    return client.get_jumps(thought_id)

@app.post("/api/thoughts", tags=["想法"])
async def create_thought(request: ThoughtCreateRequest):
    """创建新想法"""
    client = get_client()
    if request.parent_id:
        return client.create_thought(request.name, request.parent_id, 1, request.kind)
    elif request.jump_id:
        return client.create_thought(request.name, request.jump_id, 3, request.kind)
    return client.create_thought(request.name, kind=request.kind)

@app.patch("/api/thoughts/{thought_id}", tags=["想法"])
async def update_thought(thought_id: str, request: ThoughtUpdateRequest):
    """更新想法"""
    client = get_client()
    updates = []
    if request.name:
        updates.append({"op": "replace", "path": "/name", "value": request.name})
    if request.label:
        updates.append({"op": "replace", "path": "/label", "value": request.label})
    if request.color:
        updates.append({"op": "replace", "path": "/foregroundColor", "value": request.color})
    if request.type_id:
        updates.append({"op": "replace", "path": "/typeId", "value": request.type_id})
    if not updates:
        raise HTTPException(status_code=400, detail="请提供要更新的内容")
    client.update_thought(thought_id, updates)
    return {"status": "ok"}

@app.delete("/api/thoughts/{thought_id}", tags=["想法"])
async def delete_thought(thought_id: str):
    """删除想法"""
    client = get_client()
    client.delete_thought(thought_id)
    return {"status": "ok"}

# ---------- 链接 ----------
@app.post("/api/links", tags=["链接"])
async def create_link(request: LinkRequest):
    """创建链接"""
    client = get_client()
    return client.create_link(request.thought_id_a, request.thought_id_b, request.relation, request.name)

@app.delete("/api/links/{link_id}", tags=["链接"])
async def delete_link(link_id: str):
    """删除链接"""
    client = get_client()
    client.delete_link(link_id)
    return {"status": "ok"}

# ---------- 笔记 ----------
@app.get("/api/thoughts/{thought_id}/note", tags=["笔记"])
async def get_note(thought_id: str, format: str = "markdown"):
    """获取笔记 (format: markdown/html/text)"""
    client = get_client()
    return client.get_note(thought_id, format)

@app.post("/api/thoughts/{thought_id}/note", tags=["笔记"])
async def update_note(thought_id: str, request: NoteRequest):
    """更新或追加笔记"""
    client = get_client()
    if request.append:
        client.append_note(thought_id, request.content)
    else:
        client.update_note(thought_id, request.content)
    return {"status": "ok"}

# ---------- 元数据 ----------
@app.get("/api/types", tags=["元数据"])
async def get_types():
    """获取所有类型"""
    client = get_client()
    return client.get_types()

@app.get("/api/tags", tags=["元数据"])
async def get_tags():
    """获取所有标签"""
    client = get_client()
    return client.get_tags()

@app.get("/api/pins", tags=["元数据"])
async def get_pins():
    """获取置顶想法"""
    client = get_client()
    return client.get_pins()

# ---------- 附件 ----------
@app.get("/api/thoughts/{thought_id}/attachments", tags=["附件"])
async def get_attachments(thought_id: str):
    """获取附件列表"""
    client = get_client()
    return client.get_attachments(thought_id)

@app.post("/api/thoughts/{thought_id}/attachments/url", tags=["附件"])
async def add_url_attachment(thought_id: str, request: UrlAttachmentRequest):
    """添加 URL 附件"""
    client = get_client()
    return client.add_url(thought_id, request.url, request.name)

# ========== 新增接口 ==========

# ---------- 增强搜索 ----------
class SearchRawRequest(BaseModel):
    query: str
    max_results: int = 30
    only_names: bool = False

@app.post("/api/search/raw", tags=["搜索"])
async def search_raw(request: SearchRawRequest):
    """搜索想法，返回原始结果（含匹配上下文）"""
    client = get_client()
    return client.search_raw(request.query, request.max_results, request.only_names)

# ---------- 按名称查找 ----------
@app.get("/api/thoughts/by-name", tags=["想法"])
async def get_thought_by_name(name: str):
    """按名称精确查找想法"""
    client = get_client()
    result = client.get_thought_by_name(name)
    if not result:
        raise HTTPException(status_code=404, detail="想法不存在")
    return result

# ---------- 置顶操作 ----------
@app.post("/api/thoughts/{thought_id}/pin", tags=["想法"])
async def pin_thought(thought_id: str):
    """置顶想法"""
    client = get_client()
    client.pin_thought(thought_id)
    return {"status": "ok"}

@app.delete("/api/thoughts/{thought_id}/pin", tags=["想法"])
async def unpin_thought(thought_id: str):
    """取消置顶"""
    client = get_client()
    client.unpin_thought(thought_id)
    return {"status": "ok"}

# ---------- 链接增强 ----------
@app.get("/api/links/{link_id}", tags=["链接"])
async def get_link_detail(link_id: str):
    """获取链接详情"""
    client = get_client()
    return client.get_link(link_id)

@app.get("/api/links/between/{thought_id_a}/{thought_id_b}", tags=["链接"])
async def get_link_between(thought_id_a: str, thought_id_b: str):
    """获取两个想法之间的链接"""
    client = get_client()
    return client.get_link_between(thought_id_a, thought_id_b)

class LinkUpdateRequest(BaseModel):
    color: Optional[str] = None
    thickness: Optional[int] = None
    name: Optional[str] = None

@app.patch("/api/links/{link_id}", tags=["链接"])
async def update_link(link_id: str, request: LinkUpdateRequest):
    """更新链接属性"""
    client = get_client()
    updates = []
    if request.color:
        updates.append({"op": "replace", "path": "/color", "value": request.color})
    if request.thickness:
        updates.append({"op": "replace", "path": "/thickness", "value": request.thickness})
    if request.name:
        updates.append({"op": "replace", "path": "/name", "value": request.name})
    if not updates:
        raise HTTPException(status_code=400, detail="请提供要更新的内容")
    client.update_link(link_id, updates)
    return {"status": "ok"}

# ---------- 大脑统计 ----------
@app.get("/api/brain/stats", tags=["大脑"])
async def get_brain_stats():
    """获取大脑统计信息"""
    client = get_client()
    return client.get_brain_stats()

@app.get("/api/brain/modifications", tags=["大脑"])
async def get_brain_modifications(max_logs: int = 100, start_time: str = None, end_time: str = None):
    """获取大脑修改日志"""
    client = get_client()
    return client.get_brain_modifications(max_logs, start_time, end_time)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
