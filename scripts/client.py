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
        self._type_cache = None  # 类型缓存

    def _get_type_map(self) -> Dict[str, str]:
        """获取类型ID到名称的映射(带缓存)"""
        if self._type_cache is None:
            try:
                types = self.get_types()
                self._type_cache = {t['id']: t.get('name', 'Unknown') for t in types}
            except Exception as e:
                # 如果获取类型失败,使用空字典,不影响主功能
                print(f"Warning: Failed to load types: {e}")
                self._type_cache = {}
        return self._type_cache

    def _enrich_with_type_names(self, data: Any, fields: List[str] = None) -> Any:
        """为数据添加 typeName 字段
        
        Args:
            data: 要增强的数据(Dict, List 或其他)
            fields: 要增强的字段列表,默认 ['typeId']
        """
        if fields is None:
            fields = ['typeId']
        
        type_map = self._get_type_map()
        
        def _enrich_item(item: Dict) -> Dict:
            """为单个字典项添加 typeName"""
            if not isinstance(item, dict):
                return item
            for field in fields:
                if field in item and item[field]:
                    type_id = item[field]
                    type_name = type_map.get(type_id)
                    if type_name:
                        # 将 typeId 转换为 typeName 字段名
                        name_field = field.replace('Id', 'Name')
                        item[name_field] = type_name
            return item
        
        # 处理不同类型的数据
        if isinstance(data, dict):
            # 增强顶层字典
            _enrich_item(data)
            # 增强嵌套的 links 数组
            if 'links' in data and isinstance(data['links'], list):
                for link in data['links']:
                    _enrich_item(link)
            # 增强想法数组字段
            for key in ['activeThought', 'parents', 'children', 'jumps', 'siblings', 'tags']:
                if key in data:
                    if isinstance(data[key], dict):
                        _enrich_item(data[key])
                    elif isinstance(data[key], list):
                        for item in data[key]:
                            _enrich_item(item)
        elif isinstance(data, list):
            for item in data:
                _enrich_item(item)
        
        return data

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
        graph = self._request("GET", f"/thoughts/{self.brain_id}/{thought_id}/graph",
                             params={"includeSiblings": siblings})
        # 为图谱数据添加 typeName (包括 links 和 thoughts)
        return self._enrich_with_type_names(graph)

    def create_thought(self, name: str, source_id: str = None,
                       relation: int = 1, kind: int = 1, label: str = None) -> Dict:
        data = {"name": name, "kind": kind, "acType": 0}
        if label:
            data["label"] = label
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

    def append_note(self, thought_id: str, content: str, position: str = "end") -> None:
        """追加笔记内容
        
        Args:
            thought_id: 想法ID
            content: 要追加的内容
            position: 插入位置，"end"(默认)追加到末尾，"start"插入到开头
        """
        if position == "start":
            # 获取当前笔记并插入到开头
            current = self.get_note(thought_id, "markdown")
            current_text = current.get("markdown", "")
            new_content = content + "\n\n" + current_text if current_text else content
            self.update_note(thought_id, new_content)
        else:
            # 默认追加到末尾
            self._request("POST", f"/notes/{self.brain_id}/{thought_id}/append",
                           json={"markdown": content})

    def batch_replace_note(self, thought_id: str, replacements: List[List[str]]) -> Dict:
        """批量替换笔记内容
        
        Args:
            thought_id: 想法ID
            replacements: 替换对列表，格式 [["原内容1", "替换内容1"], ["原内容2", "替换内容2"]]
        
        Returns:
            包含替换统计信息的字典
        """
        # 获取当前笔记
        note = self.get_note(thought_id, "markdown")
        content = note.get("markdown", "")
        
        if not content:
            return {"replaced": 0, "patterns": 0, "error": "笔记为空"}
        
        # 批量替换
        total_replacements = 0
        patterns_matched = 0
        
        for old_text, new_text in replacements:
            if old_text in content:
                count = content.count(old_text)
                content = content.replace(old_text, new_text)
                total_replacements += count
                patterns_matched += 1
        
        # 更新笔记
        if total_replacements > 0:
            self.update_note(thought_id, content)
        
        return {
            "replaced": total_replacements,
            "patterns": patterns_matched,
            "total_patterns": len(replacements)
        }


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

    def get_link_between(self, thought_id_a: str, thought_id_b: str, detailed: bool = False) -> Dict:
        """获取两个想法之间的链接
        
        Args:
            thought_id_a: 第一个想法ID
            thought_id_b: 第二个想法ID
            detailed: 是否返回详细信息,默认 False(简化版)
        
        Returns:
            简化版包含: relation, meaning, thickness, name
            详细版包含: 所有字段
        """
        link = self._request("GET", f"/links/{self.brain_id}/{thought_id_a}/{thought_id_b}")
        
        if not detailed and link:
            # 简化版:只返回关键字段
            return {
                "id": link.get("id"),
                "relation": link.get("relation"),
                "meaning": link.get("meaning"),
                "thickness": link.get("thickness"),
                "name": link.get("name", ""),
                "color": link.get("color"),
                "typeId": link.get("typeId")
            }
        
        return link

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
            depth: 探索深度(1-3层,默认2层)
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
                    "typeName": thought.get("typeName"),  # 从增强后的 graph 获取
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
        """获取想法的完整上下文(详情 + 笔记 + 关联节点摘要)
        
        Args:
            thought_id: 想法ID
        """
        # 1. 获取图谱(包含想法详情和所有关联,已自动增强 typeName)
        graph = self.get_graph(thought_id, siblings=True)
        thought = graph.get("activeThought", {})
        
        # 2. 获取笔记
        try:
            note = self.get_note(thought_id, "markdown")
            note_content = note.get("markdown", "") if note else ""
        except:
            note_content = ""
        
        # 3. 简化关联节点信息(保留 typeName)
        def simplify_thoughts(thoughts: List[Dict]) -> List[Dict]:
            return [{
                "id": t.get("id"),
                "name": t.get("name"),
                "kind": t.get("kind"),
                "typeId": t.get("typeId"),
                "typeName": t.get("typeName")  # 添加类型名称
            } for t in thoughts]
        
        # 4. 组装完整上下文
        context = {
            "thought": {
                "id": thought.get("id"),
                "name": thought.get("name"),
                "kind": thought.get("kind"),
                "label": thought.get("label"),
                "typeId": thought.get("typeId"),
                "typeName": thought.get("typeName"),  # 添加类型名称
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

    def recent_thoughts(self, days: int = 7, max_results: int = 20) -> List[Dict]:
        """获取最近修改的想法
        
        Args:
            days: 查询最近多少天，默认7天
            max_results: 最大结果数，默认20
        """
        from datetime import datetime, timedelta
        
        # 计算开始时间
        start_time = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        
        # 获取修改日志
        modifications = self.get_brain_modifications(max_logs=max_results * 5, start_time=start_time)
        
        # 提取想法ID并去重
        # 修改日志结构: sourceType=2 表示 Thought，extraAId/sourceId 包含想法ID
        seen_ids = set()
        results = []
        
        for mod in modifications:
            # extraAType=2 表示这是一个想法相关的修改
            # sourceType=2 也表示想法
            thought_id = None
            if mod.get("extraAType") == 2:
                thought_id = mod.get("extraAId")
            elif mod.get("sourceType") == 2:
                thought_id = mod.get("sourceId")
            
            # 跳过无效ID
            if not thought_id or thought_id == "00000000-0000-0000-0000-000000000000":
                continue
            if thought_id in seen_ids:
                continue
            seen_ids.add(thought_id)
            
            try:
                thought = self.get_thought(thought_id)
                results.append({
                    "id": thought.get("id"),
                    "name": thought.get("name"),
                    "kind": thought.get("kind"),
                    "modifiedAt": thought.get("modificationDateTime"),
                    "modType": mod.get("modType")
                })
            except:
                continue
            
            if len(results) >= max_results:
                break
        
        return results

    def find_related(self, keywords: List[str], max_results: int = 10) -> List[Dict]:
        """根据多个关键词查找相关想法，按匹配度排序
        
        Args:
            keywords: 关键词列表
            max_results: 最大结果数，默认10
        """
        all_results = {}
        
        for keyword in keywords:
            if not keyword.strip():
                continue
            results = self.search(keyword.strip(), max_results=max_results * 2)
            
            for r in results:
                thought_id = r.get("id")
                if not thought_id:
                    continue
                    
                if thought_id in all_results:
                    all_results[thought_id]["score"] += 1
                    all_results[thought_id]["matched_keywords"].append(keyword)
                else:
                    all_results[thought_id] = {
                        "id": thought_id,
                        "name": r.get("name"),
                        "kind": r.get("kind"),
                        "typeId": r.get("typeId"),
                        "score": 1,
                        "matched_keywords": [keyword]
                    }
        
        # 按匹配分数排序（匹配更多关键词的排前面）
        sorted_results = sorted(
            all_results.values(), 
            key=lambda x: x["score"], 
            reverse=True
        )
        
        return sorted_results[:max_results]

