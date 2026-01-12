import sys
import json
import os
from pathlib import Path
from typing import Optional, Union, Dict, List, Any

# 添加 scripts 目录到路径
sys.path.append(str(Path(__file__).parent / "scripts"))

from fastmcp import FastMCP
from fastmcp.server.auth.providers.debug import DebugTokenVerifier
from client import TheBrainClient

# ========== MCP 认证 ==========
def get_api_key() -> str:
    """从环境变量获取 THEBRAIN_API_KEY"""
    return os.getenv("THEBRAIN_API_KEY", "")

def validate_bearer_token(token: str) -> bool:
    """验证 Bearer Token（与 FastAPI 使用相同的 API Key）"""
    expected_token = get_api_key()
    if not expected_token:
        # 如果没有设置 API Key，则不启用认证（开发模式）
        return True
    return token == expected_token

# 创建认证验证器
auth_verifier = DebugTokenVerifier(
    validate=validate_bearer_token,
    client_id="thebrain-mcp-client",
    scopes=["read", "write"]
)

# 创建带认证的 MCP 服务器
mcp = FastMCP("TheBrain", auth=auth_verifier)
client = TheBrainClient()

# ========== n8n 兼容性 ==========
# n8n 的 MCP 节点会传入额外参数，我们接受但从 schema 中隐藏它们
# 使用 exclude_args 让 AI 看不到这些参数
N8N_COMPAT_ARGS = ["sessionId", "action", "chatInput", "toolCallId"]

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def search_thoughts(
    query: str, 
    n: int = 30,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """搜索 TheBrain 中的想法 (Thoughts)
    
    Args:
        query: 搜索关键词
        n: 返回结果数量，默认30
    """
    results = client.search(query, n)
    return {"results": results, "count": len(results) if isinstance(results, list) else 0}

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def get_thought(
    thought_id: str,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """获取指定想法的详细信息
    
    Args:
        thought_id: 想法的唯一ID
    """
    return client.get_thought(thought_id)

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def get_graph(
    thought_id: str, 
    siblings: bool = False,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """获取想法的图谱关系（子、父、跳转等）
    
    Args:
        thought_id: 想法的唯一ID
        siblings: 是否包含兄弟节点，默认False
    """
    return client.get_graph(thought_id, siblings)

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def create_thought(
    name: str, 
    parent_id: Optional[str] = None, 
    jump_id: Optional[str] = None, 
    kind: int = 1,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """创建新想法。可以指定父想法或跳转连接。
    
    Args:
        name: 想法名称
        parent_id: 父想法ID（可选）
        jump_id: 跳转连接的想法ID（可选）
        kind: 想法类型 - 1=普通, 2=类型, 4=标签
    """
    if parent_id:
        return client.create_thought(name, parent_id, 1, kind)
    elif jump_id:
        return client.create_thought(name, jump_id, 3, kind)
    return client.create_thought(name, kind=kind)

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def update_thought(
    thought_id: str, 
    name: Optional[str] = None, 
    label: Optional[str] = None, 
    color: Optional[str] = None, 
    type_id: Optional[str] = None,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """更新想法。支持更改名称、标签、颜色或类型。
    
    Args:
        thought_id: 想法的唯一ID
        name: 新名称（可选）
        label: 新标签（可选）
        color: 新颜色（可选）
        type_id: 新类型ID（可选）
    """
    updates = []
    if name: updates.append({"op": "replace", "path": "/name", "value": name})
    if label: updates.append({"op": "replace", "path": "/label", "value": label})
    if color: updates.append({"op": "replace", "path": "/foregroundColor", "value": color})
    if type_id: updates.append({"op": "replace", "path": "/typeId", "value": type_id})
    if not updates:
        return {"status": "error", "message": "请提供要更新的内容"}
    client.update_thought(thought_id, updates)
    return {"status": "ok", "message": "已更新"}

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def delete_thought(
    thought_id: str,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """删除指定的想法
    
    Args:
        thought_id: 想法的唯一ID
    """
    client.delete_thought(thought_id)
    return {"status": "ok", "message": "已删除"}

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def create_link(
    thought_id_a: str, 
    thought_id_b: str, 
    relation: int = 3, 
    name: Optional[str] = None,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """创建两个想法之间的链接
    
    Args:
        thought_id_a: 第一个想法的ID
        thought_id_b: 第二个想法的ID
        relation: 关系类型 - 1=子, 2=父, 3=跳转
        name: 链接名称（可选）
    """
    return client.create_link(thought_id_a, thought_id_b, relation, name)

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def delete_link(
    link_id: str,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """删除想法之间的链接
    
    Args:
        link_id: 链接的唯一ID
    """
    client.delete_link(link_id)
    return {"status": "ok", "message": "链接已删除"}

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def get_note(
    thought_id: str, 
    format: str = "markdown",
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """获取想法的笔记内容
    
    Args:
        thought_id: 想法的唯一ID
        format: 输出格式，默认markdown
    """
    return client.get_note(thought_id, format)

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def update_note(
    thought_id: str, 
    content: str,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """【警告：覆盖操作】更新想法的笔记。这会覆盖原有的所有笔记内容！
    
    Args:
        thought_id: 想法的唯一ID
        content: 新的笔记内容
    """
    client.update_note(thought_id, content)
    return {"status": "ok", "message": "笔记已更新（覆盖）"}

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def append_note(
    thought_id: str, 
    content: str,
    position: str = "end",
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """【推荐】追加笔记。可选择追加到末尾或插入到开头。
    
    Args:
        thought_id: 想法的唯一ID
        content: 要追加的笔记内容
        position: 插入位置，"end"(默认)追加到末尾，"start"插入到开头
    """
    client.append_note(thought_id, content, position)
    return {"status": "ok", "message": f"笔记已追加到{position}", "position": position}

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def batch_replace_note(
    thought_id: str,
    replacements: str,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """批量替换笔记内容，高效处理多个替换模式
    
    Args:
        thought_id: 想法的唯一ID
        replacements: JSON字符串格式的替换对，如: '[["旧文本1","新文本1"],["旧文本2","新文本2"]]'
    """
    import json
    try:
        replacement_list = json.loads(replacements)
    except json.JSONDecodeError:
        return {"status": "error", "message": "replacements 参数必须是有效的 JSON 数组"}
    
    result = client.batch_replace_note(thought_id, replacement_list)
    return {"status": "ok", **result}


@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def list_metadata(
    category: str,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """列出 TheBrain 的元数据
    
    Args:
        category: 类别，可选: 'types', 'tags', 'pins'
    """
    if category == 'types':
        data = client.get_types()
        return {"category": "types", "items": data, "count": len(data) if isinstance(data, list) else 0}
    if category == 'tags':
        data = client.get_tags()
        return {"category": "tags", "items": data, "count": len(data) if isinstance(data, list) else 0}
    if category == 'pins':
        data = client.get_pins()
        return {"category": "pins", "items": data, "count": len(data) if isinstance(data, list) else 0}
    return {"error": "无效的类别。请使用 'types', 'tags' 或 'pins'"}

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def import_structure(
    parent_id: str, 
    data: str,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """导入结构化数据。data 应为 JSON 字符串。
    
    Args:
        parent_id: 父想法的ID
        data: JSON字符串格式的结构数据，例如: {"name": "Root", "children": ["Child1", {"name": "Child2"}]}
    """
    try:
        parsed_data = json.loads(data)
    except json.JSONDecodeError:
        return {"status": "error", "message": f"JSON 解析失败: {data[:100]}..."}
    
    client.create_structure(parent_id, parsed_data)
    return {"status": "ok", "message": "结构化导入完成"}


# ========== 知识管理增强工具 ==========

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def search_by_type(
    query: str = "",
    type_id: Optional[str] = None,
    tag_id: Optional[str] = None,
    max_results: int = 30,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """按类型或标签过滤搜索想法
    
    Args:
        query: 搜索关键词（可选，为空则只按类型/标签过滤）
        type_id: 类型ID，可通过 list_metadata('types') 获取
        tag_id: 标签ID，可通过 list_metadata('tags') 获取
        max_results: 最大结果数，默认30
    """
    results = client.search_by_type(query, type_id, tag_id, max_results)
    return {"results": results, "count": len(results)}

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def explore_neighbors(
    thought_id: str,
    depth: int = 2,
    include_notes: bool = False,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """多层级探索想法的邻居节点，发现知识关联
    
    Args:
        thought_id: 起始想法的ID
        depth: 探索深度（1-3层），默认2层
        include_notes: 是否包含笔记摘要（仅第1层），默认False
    """
    result = client.explore_neighbors(thought_id, depth, include_notes)
    return result

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def get_context(
    thought_id: str,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """获取想法的完整上下文（详情 + 笔记 + 所有关联节点）
    
    Args:
        thought_id: 想法的ID
    """
    return client.get_context(thought_id)

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def recent_thoughts(
    days: int = 7,
    max_results: int = 20,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """获取最近修改的想法，了解知识库的最新动态
    
    Args:
        days: 查询最近多少天，默认7天
        max_results: 最大结果数，默认20
    """
    results = client.recent_thoughts(days, max_results)
    return {"results": results, "count": len(results), "days": days}

@mcp.tool(exclude_args=N8N_COMPAT_ARGS)
def find_related(
    keywords: str,
    max_results: int = 10,
    sessionId: Optional[str] = None,
    action: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> dict:
    """根据多个关键词查找相关想法，按匹配度排序
    
    Args:
        keywords: 关键词，多个关键词用逗号分隔（如："AI,机器学习,自动化"）
        max_results: 最大结果数，默认10
    """
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
    results = client.find_related(keyword_list, max_results)
    return {"results": results, "count": len(results), "keywords": keyword_list}


@mcp.resource("thought://{id}")
def get_thought_resource(id: str) -> str:
    """以资源形式获取想法内容"""
    thought = client.get_thought(id)
    note = client.get_note(id, "markdown")
    return f"# {thought.get('name')}\n\n{note.get('markdown', '')}"

@mcp.prompt()
def summarize_thought(
    thought_id: str,
    sessionId: Optional[str] = None,
    chatInput: Optional[str] = None,
    toolCallId: Optional[str] = None
) -> str:
    """生成一个用于总结特定想法的提示词
    
    Args:
        thought_id: 想法的唯一ID
    """
    return f"请帮我总结一下这个想法的内容：thought://{thought_id}"

if __name__ == "__main__":
    mcp.run()
