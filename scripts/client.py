import os
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

def _find_project_root() -> Path:
    """向上查找包含 .env 或 .claude 目录的项目根目录"""
    current = Path.cwd()
    for _ in range(10):
        if (current / ".env").exists():
            return current
        if (current / ".claude").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return Path.cwd()

def _load_env():
    """自动加载 .env 文件"""
    possible_paths = [
        _find_project_root() / ".env",
        Path.cwd() / ".env",
        Path.home() / ".env",
    ]
    for env_path in possible_paths:
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, _, value = line.partition('=')
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and key not in os.environ:
                            os.environ[key] = value
            break

class TheBrainClient:
    """TheBrain API 客户端"""

    def __init__(self):
        _load_env()
        self.base_url = "https://api.bra.in"
        self.api_key = os.environ.get("THEBRAIN_API_KEY")
        self.brain_id = os.environ.get("THEBRAIN_BRAIN_ID")
        if not self.api_key:
            raise ValueError("THEBRAIN_API_KEY 未设置")
        if not self.brain_id:
            raise ValueError("THEBRAIN_BRAIN_ID 未设置")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json() if response.text else None

    def _patch(self, endpoint: str, updates: List[Dict]) -> Any:
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json-patch+json"
        }
        response = requests.patch(url, headers=headers, json=updates)
        response.raise_for_status()
        return response.json() if response.text else None

    def search(self, query: str, max_results: int = 30, only_names: bool = False) -> List[Dict]:
        """搜索想法，返回丰富的字段信息"""
        params = {"queryText": query, "maxResults": max_results, "onlySearchThoughtNames": only_names}
        results = self._request("GET", f"/search/{self.brain_id}", params=params)
        if not results:
            return []
        # 保留更多有用字段
        return [{
            "id": r.get("sourceThought", {}).get("id"),
            "name": r.get("sourceThought", {}).get("name"),
            "kind": r.get("sourceThought", {}).get("kind"),
            "label": r.get("sourceThought", {}).get("label"),
            "typeId": r.get("sourceThought", {}).get("typeId"),
            "acType": r.get("sourceThought", {}).get("acType"),
            "foregroundColor": r.get("sourceThought", {}).get("foregroundColor"),
            "modificationDateTime": r.get("sourceThought", {}).get("modificationDateTime"),
        } for r in results if r.get("sourceThought")]

    def search_raw(self, query: str, max_results: int = 30, only_names: bool = False) -> List[Dict]:
        """搜索想法，返回原始结果（含匹配上下文）"""
        params = {"queryText": query, "maxResults": max_results, "onlySearchThoughtNames": only_names}
        return self._request("GET", f"/search/{self.brain_id}", params=params) or []

    def get_thought(self, thought_id: str) -> Dict:
        return self._request("GET", f"/thoughts/{self.brain_id}/{thought_id}")

    def get_graph(self, thought_id: str, siblings: bool = False) -> Dict:
        return self._request("GET", f"/thoughts/{self.brain_id}/{thought_id}/graph",
                             params={"includeSiblings": siblings})

    def create_thought(self, name: str, source_id: str = None,
                       relation: int = 1, kind: int = 1) -> Dict:
        data = {"name": name, "kind": kind, "acType": 0}
        if source_id:
            data["sourceThoughtId"] = source_id
            data["relation"] = relation
        print(f"DEBUG: create_thought payload: {data}")
        return self._request("POST", f"/thoughts/{self.brain_id}", json=data)

    def update_thought(self, thought_id: str, updates: List[Dict]) -> None:
        self._patch(f"/thoughts/{self.brain_id}/{thought_id}", updates)

    def delete_thought(self, thought_id: str) -> None:
        self._request("DELETE", f"/thoughts/{self.brain_id}/{thought_id}")

    def get_children(self, thought_id: str) -> List[Dict]:
        graph = self.get_graph(thought_id)
        return graph.get("children", [])

    def get_parents(self, thought_id: str) -> List[Dict]:
        graph = self.get_graph(thought_id)
        return graph.get("parents", [])

    def get_jumps(self, thought_id: str) -> List[Dict]:
        graph = self.get_graph(thought_id)
        return graph.get("jumps", [])

    def create_link(self, id_a: str, id_b: str, relation: int = 3,
                    name: str = None) -> Dict:
        data = {"thoughtIdA": id_a, "thoughtIdB": id_b, "relation": relation}
        if name:
            data["name"] = name
        return self._request("POST", f"/links/{self.brain_id}", json=data)

    def delete_link(self, link_id: str) -> None:
        self._request("DELETE", f"/links/{self.brain_id}/{link_id}")

    def get_note(self, thought_id: str, fmt: str = "markdown") -> Dict:
        ep = f"/notes/{self.brain_id}/{thought_id}"
        if fmt == "html":
            ep += "/html"
        elif fmt == "text":
            ep += "/text"
        return self._request("GET", ep)

    def update_note(self, thought_id: str, content: str) -> None:
        self._request("POST", f"/notes/{self.brain_id}/{thought_id}/update",
                       json={"markdown": content})

    def append_note(self, thought_id: str, content: str) -> None:
        self._request("POST", f"/notes/{self.brain_id}/{thought_id}/append",
                       json={"markdown": content})

    def get_types(self) -> List[Dict]:
        return self._request("GET", f"/thoughts/{self.brain_id}/types")

    def get_tags(self) -> List[Dict]:
        return self._request("GET", f"/thoughts/{self.brain_id}/tags")

    def get_pins(self) -> List[Dict]:
        return self._request("GET", f"/thoughts/{self.brain_id}/pins")

    def get_attachments(self, thought_id: str) -> List[Dict]:
        return self._request("GET", f"/thoughts/{self.brain_id}/{thought_id}/attachments")

    def add_url(self, thought_id: str, url: str, name: str = None) -> Dict:
        data = {"url": url}
        if name:
            data["name"] = name
        return self._request("POST", f"/attachments/{self.brain_id}/{thought_id}/url", json=data)

    # ========== 新增方法 ==========

    def get_thought_by_name(self, name: str) -> Optional[Dict]:
        """按名称精确查找想法"""
        result = self._request("GET", f"/thoughts/{self.brain_id}", params={"nameExact": name})
        return result if result else None

    def pin_thought(self, thought_id: str) -> None:
        """置顶想法"""
        self._request("POST", f"/thoughts/{self.brain_id}/{thought_id}/pin")

    def unpin_thought(self, thought_id: str) -> None:
        """取消置顶"""
        self._request("DELETE", f"/thoughts/{self.brain_id}/{thought_id}/pin")

    def get_link(self, link_id: str) -> Dict:
        """获取链接详情"""
        return self._request("GET", f"/links/{self.brain_id}/{link_id}")

    def get_link_between(self, thought_id_a: str, thought_id_b: str) -> Dict:
        """获取两个想法之间的链接"""
        return self._request("GET", f"/links/{self.brain_id}/{thought_id_a}/{thought_id_b}")

    def update_link(self, link_id: str, updates: List[Dict]) -> None:
        """更新链接属性 (使用 JSON Patch 格式)"""
        self._patch(f"/links/{self.brain_id}/{link_id}", updates)

    def get_brain_stats(self) -> Dict:
        """获取大脑统计信息"""
        return self._request("GET", f"/brains/{self.brain_id}/statistics")

    def get_brain_modifications(self, max_logs: int = 100, start_time: str = None, end_time: str = None) -> List[Dict]:
        """获取大脑修改日志"""
        params = {"maxLogs": max_logs}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return self._request("GET", f"/brains/{self.brain_id}/modifications", params=params) or []

    def create_structure(self, parent_id: str, data: Union[Dict, List, str, int, float]) -> None:
        """递归导入结构化数据，支持 List/Dict/Primitives"""
        # Case 1: List -> iterate
        if isinstance(data, list):
            for item in data:
                self.create_structure(parent_id, item)
            return

        if isinstance(data, (str, int, float)):
             t = self.create_thought(str(data))
             self.create_link(parent_id, t["id"], 1)
             return

        # Case 3: Dict -> create complex thought
        if isinstance(data, dict):
             # 1. Prepare creation args
             name = data.get("name", "未命名")
             kind = data.get("kind", 1)
             
             # Create thought (orphan first)
             new_thought = self.create_thought(name, kind=kind)
             new_id = new_thought["id"]
             
             # Link to parent explicitly
             self.create_link(parent_id, new_id, 1)  # 1=Child relation (Parent->Child)
             
             # 2. Update properties
             updates = []
             if "label" in data:
                 updates.append({"op": "replace", "path": "/label", "value": data["label"]})
             if "color" in data:
                 updates.append({"op": "replace", "path": "/foregroundColor", "value": data["color"]})
             if "typeId" in data:
                 updates.append({"op": "replace", "path": "/typeId", "value": data["typeId"]})
             if "acType" in data:
                 updates.append({"op": "replace", "path": "/acType", "value": data["acType"]})
             
             if updates:
                 self.update_thought(new_id, updates)
                 
             # 3. Update note
             if "note" in data:
                 self.update_note(new_id, data["note"])
                 
             # 4. Handle children recursively
             children = data.get("children", [])
             if children:
                 self.create_structure(new_id, children)

    # ========== 知识管理增强方法 ==========

    def search_by_type(self, query: str = "", type_id: str = None, tag_id: str = None, 
                       max_results: int = 30) -> List[Dict]:
        """按类型或标签过滤搜索
        
        Args:
            query: 搜索关键词（可选，为空则只按类型/标签过滤）
            type_id: 类型ID（可选）
            tag_id: 标签ID（可选）
            max_results: 最大结果数
        """
        # 先获取所有匹配的结果
        if query:
            results = self.search(query, max_results=max_results * 3)  # 获取更多结果用于过滤
        else:
            # 没有查询词时，获取该类型/标签下的所有想法
            # 通过遍历类型/标签的子节点来实现
            results = []
            if type_id:
                graph = self.get_graph(type_id)
                # 类型的实例通常作为该类型节点的子节点或关联
                for child in graph.get("children", []):
                    child["_source"] = "type_child"
                    results.append(child)
            if tag_id:
                graph = self.get_graph(tag_id)
                for child in graph.get("children", []):
                    child["_source"] = "tag_child"
                    results.append(child)
            return results[:max_results]
        
        # 过滤结果
        filtered = []
        for r in results:
            # 按类型过滤
            if type_id and r.get("typeId") != type_id:
                continue
            # 按标签过滤（需要检查想法是否有该标签）
            if tag_id:
                # 获取想法详情检查标签
                try:
                    graph = self.get_graph(r["id"])
                    tag_ids = [t.get("id") for t in graph.get("tags", [])]
                    if tag_id not in tag_ids:
                        continue
                except:
                    continue
            filtered.append(r)
            if len(filtered) >= max_results:
                break
        
        return filtered

    def explore_neighbors(self, thought_id: str, depth: int = 2, 
                          include_notes: bool = False) -> Dict:
        """多层级探索想法的邻居节点
        
        Args:
            thought_id: 起始想法ID
            depth: 探索深度（1-3层，默认2层）
            include_notes: 是否包含笔记摘要
        """
        depth = min(max(depth, 1), 3)  # 限制在 1-3 层
        visited = set()
        
        def _explore(tid: str, current_depth: int) -> Dict:
            if tid in visited or current_depth > depth:
                return None
            visited.add(tid)
            
            try:
                graph = self.get_graph(tid, siblings=False)
                thought = graph.get("activeThought", {})
                
                result = {
                    "id": thought.get("id"),
                    "name": thought.get("name"),
                    "kind": thought.get("kind"),
                    "typeId": thought.get("typeId"),
                    "depth": current_depth
                }
                
                # 添加笔记摘要
                if include_notes and current_depth == 1:
                    try:
                        note = self.get_note(tid, "text")
                        note_text = note.get("text", "") if note else ""
                        result["note_preview"] = note_text[:200] + "..." if len(note_text) > 200 else note_text
                    except:
                        result["note_preview"] = ""
                
                # 递归探索子节点
                if current_depth < depth:
                    result["children"] = []
                    for child in graph.get("children", [])[:10]:  # 限制每层最多10个
                        child_result = _explore(child.get("id"), current_depth + 1)
                        if child_result:
                            result["children"].append(child_result)
                    
                    result["parents"] = []
                    for parent in graph.get("parents", [])[:5]:  # 父节点少一些
                        parent_result = _explore(parent.get("id"), current_depth + 1)
                        if parent_result:
                            result["parents"].append(parent_result)
                    
                    result["jumps"] = []
                    for jump in graph.get("jumps", [])[:5]:  # 跳跃节点少一些
                        jump_result = _explore(jump.get("id"), current_depth + 1)
                        if jump_result:
                            result["jumps"].append(jump_result)
                
                return result
            except Exception as e:
                return {"id": tid, "error": str(e)}
        
        return _explore(thought_id, 1)

    def get_context(self, thought_id: str) -> Dict:
        """获取想法的完整上下文（详情 + 笔记 + 关联节点摘要）
        
        Args:
            thought_id: 想法ID
        """
        # 1. 获取图谱（包含想法详情和所有关联）
        graph = self.get_graph(thought_id, siblings=True)
        thought = graph.get("activeThought", {})
        
        # 2. 获取笔记
        try:
            note = self.get_note(thought_id, "markdown")
            note_content = note.get("markdown", "") if note else ""
        except:
            note_content = ""
        
        # 3. 简化关联节点信息
        def simplify_thoughts(thoughts: List[Dict]) -> List[Dict]:
            return [{
                "id": t.get("id"),
                "name": t.get("name"),
                "kind": t.get("kind")
            } for t in thoughts]
        
        # 4. 组装完整上下文
        context = {
            "thought": {
                "id": thought.get("id"),
                "name": thought.get("name"),
                "kind": thought.get("kind"),
                "label": thought.get("label"),
                "typeId": thought.get("typeId"),
                "createdAt": thought.get("creationDateTime"),
                "modifiedAt": thought.get("modificationDateTime"),
            },
            "note": note_content,
            "relations": {
                "parents": simplify_thoughts(graph.get("parents", [])),
                "children": simplify_thoughts(graph.get("children", [])),
                "jumps": simplify_thoughts(graph.get("jumps", [])),
                "siblings": simplify_thoughts(graph.get("siblings", [])),
                "tags": simplify_thoughts(graph.get("tags", [])),
            },
            "stats": {
                "parent_count": len(graph.get("parents", [])),
                "child_count": len(graph.get("children", [])),
                "jump_count": len(graph.get("jumps", [])),
                "sibling_count": len(graph.get("siblings", [])),
                "tag_count": len(graph.get("tags", [])),
                "attachment_count": len(graph.get("attachments", [])),
            }
        }
        
        return context
