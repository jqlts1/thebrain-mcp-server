import sys
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.append(str(Path(__file__).parent / "scripts"))

from fastmcp import FastMCP
from client import TheBrainClient

from typing import Any

mcp = FastMCP("TheBrain")
client = TheBrainClient()

@mcp.tool()
def search_thoughts(query: str, n: int = 30, **kwargs: Any):
    """搜索 TheBrain 中的想法 (Thoughts)"""
    return client.search(query, n)

@mcp.tool()
def get_thought(thought_id: str, **kwargs: Any):
    """获取指定想法的详细信息"""
    return client.get_thought(thought_id)

@mcp.tool()
def get_graph(thought_id: str, siblings: bool = False, **kwargs: Any):
    """获取想法的图谱关系（子、父、跳转等）"""
    return client.get_graph(thought_id, siblings)

@mcp.tool()
def create_thought(name: str, parent_id: str = None, jump_id: str = None, kind: int = 1, **kwargs: Any):
    """创建新想法。可以指定父想法或跳转连接。kind: 1=普通, 2=类型, 4=标签"""
    if parent_id:
        return client.create_thought(name, parent_id, 1, kind)
    elif jump_id:
        return client.create_thought(name, jump_id, 3, kind)
    return client.create_thought(name, kind=kind)

@mcp.tool()
def update_thought(thought_id: str, name: str = None, label: str = None, color: str = None, type_id: str = None, **kwargs: Any):
    """更新想法。支持更改名称、标签、颜色或类型。"""
    updates = []
    if name: updates.append({"op": "replace", "path": "/name", "value": name})
    if label: updates.append({"op": "replace", "path": "/label", "value": label})
    if color: updates.append({"op": "replace", "path": "/foregroundColor", "value": color})
    if type_id: updates.append({"op": "replace", "path": "/typeId", "value": type_id})
    if not updates:
        return "请提供要更新的内容"
    client.update_thought(thought_id, updates)
    return "已更新"

@mcp.tool()
def delete_thought(thought_id: str, **kwargs: Any):
    """删除指定的想法"""
    client.delete_thought(thought_id)
    return "已删除"

@mcp.tool()
def manage_link(thought_id_a: str, thought_id_b: str, relation: int = 3, name: str = None, action: str = "create", link_id: str = None, **kwargs: Any):
    """管理想法之间的链接。action: 'create' 或 'delete'。relation: 1=子, 2=父, 3=跳转"""
    if action == "delete":
        if not link_id: return "删除链接需要 link_id"
        client.delete_link(link_id)
        return "链接已删除"
    return client.create_link(thought_id_a, thought_id_b, relation, name)

@mcp.tool()
def get_note(thought_id: str, format: str = "markdown", **kwargs: Any):
    """获取想法的笔记内容"""
    return client.get_note(thought_id, format)

@mcp.tool()
def update_note(thought_id: str, content: str, **kwargs: Any):
    """【警告：覆盖操作】更新想法的笔记。这会覆盖原有的所有笔记内容！"""
    client.update_note(thought_id, content)
    return "笔记已更新（覆盖）"

@mcp.tool()
def append_note(thought_id: str, content: str, **kwargs: Any):
    """【推荐】追加笔记。将新内容追加到现有笔记的末尾，不会覆盖原有内容。"""
    client.append_note(thought_id, content)
    return "笔记已追加"

@mcp.tool()
def list_metadata(category: str, **kwargs: Any):
    """列出 TheBrain 的元数据。category 可选: 'types', 'tags', 'pins'"""
    if category == 'types': return client.get_types()
    if category == 'tags': return client.get_tags()
    if category == 'pins': return client.get_pins()
    return "无效的类别。请使用 'types', 'tags' 或 'pins'"

@mcp.resource("thought://{id}")
def get_thought_resource(id: str) -> str:
    """以资源形式获取想法内容"""
    thought = client.get_thought(id)
    note = client.get_note(id, "markdown")
    return f"# {thought.get('name')}\n\n{note.get('markdown', '')}"

@mcp.prompt()
def summarize_thought(thought_id: str, **kwargs: Any):
    """生成一个用于总结特定想法的提示词"""
    return f"请帮我总结一下这个想法的内容：thought://{thought_id}"

if __name__ == "__main__":
    mcp.run()
