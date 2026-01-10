import os
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any

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
        return self._request("POST", f"/thoughts/{self.brain_id}", json=data)

    def update_thought(self, thought_id: str, updates: List[Dict]) -> None:
        self._patch(f"/thoughts/{self.brain_id}/{thought_id}", updates)

    def delete_thought(self, thought_id: str) -> None:
        self._request("DELETE", f"/thoughts/{self.brain_id}/{thought_id}")

    def get_children(self, thought_id: str) -> List[Dict]:
        graph = self.get_graph(thought_id)
        children = []
        for link in graph.get("links", []):
            if link.get("relation") == 1 and link.get("thoughtIdA") == thought_id:
                tid = link.get("thoughtIdB")
                for t in graph.get("thoughts", []):
                    if t.get("id") == tid:
                        children.append({"id": t["id"], "name": t.get("name")})
                        break
        return children

    def get_parents(self, thought_id: str) -> List[Dict]:
        graph = self.get_graph(thought_id)
        parents = []
        for link in graph.get("links", []):
            if link.get("relation") == 1 and link.get("thoughtIdB") == thought_id:
                tid = link.get("thoughtIdA")
                for t in graph.get("thoughts", []):
                    if t.get("id") == tid:
                        parents.append({"id": t["id"], "name": t.get("name")})
                        break
        return parents

    def get_jumps(self, thought_id: str) -> List[Dict]:
        graph = self.get_graph(thought_id)
        jumps = []
        for link in graph.get("links", []):
            if link.get("relation") == 3:
                tid = link.get("thoughtIdB") if link.get("thoughtIdA") == thought_id else link.get("thoughtIdA")
                for t in graph.get("thoughts", []):
                    if t.get("id") == tid:
                        jumps.append({"id": t["id"], "name": t.get("name")})
                        break
        return jumps

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
