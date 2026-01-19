"""
SRS 服务层

提供完整的间隔重复功能，包括同步、获取卡片、复习等。
"""

import sys
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Optional, Any

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from client import TheBrainClient
from . import db
from .algorithm import calculate_next_review, estimate_next_intervals, get_quality_label


class SRSService:
    """SRS 服务类"""
    
    FLASHCARD_TAG_NAME = "FlashCard"  # 标签名称
    
    def __init__(self):
        self.client = TheBrainClient()
        self._tag_id_cache = None
    
    def _get_flashcard_tag_id(self) -> Optional[str]:
        """获取 FlashCard 标签的 ID"""
        # 尝试从缓存获取
        if self._tag_id_cache:
            return self._tag_id_cache
        
        # 尝试从数据库获取
        cached = db.get_meta("flashcard_tag_id")
        if cached:
            self._tag_id_cache = cached
            return cached
        
        # 从 TheBrain 获取
        tags = self.client.get_tags()
        for tag in tags:
            if tag.get("name") == self.FLASHCARD_TAG_NAME:
                tag_id = tag.get("id")
                db.set_meta("flashcard_tag_id", tag_id)
                self._tag_id_cache = tag_id
                return tag_id
        
        return None
    
    def sync(self, force_full: bool = False) -> Dict[str, Any]:
        """
        从 TheBrain 同步 FlashCard 标签的节点
        
        Args:
            force_full: 是否强制全量同步
        
        Returns:
            同步结果统计
        """
        tag_id = self._get_flashcard_tag_id()
        if not tag_id:
            return {
                "success": False,
                "error": f"未找到 '{self.FLASHCARD_TAG_NAME}' 标签，请先在 TheBrain 中创建",
                "added": 0,
                "updated": 0
            }
        
        # 获取上次同步时间
        last_sync = None if force_full else db.get_meta("last_sync_time")
        
        # 方法1: 通过标签的 graph 获取关联节点
        graph = self.client.get_graph(tag_id)
        
        # 收集所有关联的节点 (children + jumps)
        # TheBrain 标签可能通过 children 或 jumps 关联
        related_thoughts = []
        related_thoughts.extend(graph.get("children", []))
        related_thoughts.extend(graph.get("jumps", []))
        
        # 方法2: 获取最近修改的节点 (解决 API 同步延迟问题)
        # 检查最近修改的节点是否有 FlashCard 标签
        recent = self.client.recent_thoughts(days=7, max_results=50)
        
        # 方法3: 也搜索一下带标签的节点 (双重保险)
        search_results = self.client.search(self.FLASHCARD_TAG_NAME, max_results=100)
        
        # 收集所有节点 ID
        seen_ids = set()
        thoughts = []
        
        # 从标签关联节点获取
        for thought in related_thoughts:
            tid = thought.get("id")
            if tid and tid not in seen_ids:
                seen_ids.add(tid)
                thoughts.append(thought)
        
        # 合并搜索结果和最近修改的节点
        candidates = []
        candidates.extend(search_results)
        candidates.extend(recent)
        
        # 检查候选节点是否真的有 FlashCard 标签
        for thought in candidates:
            tid = thought.get("id")
            if tid and tid not in seen_ids and tid != tag_id:
                # 验证这个节点是否确实有 FlashCard 标签
                try:
                    node_graph = self.client.get_graph(tid)
                    node_tags = node_graph.get("tags", [])
                    if any(t.get("id") == tag_id for t in node_tags):
                        seen_ids.add(tid)
                        # 补充 modificationDateTime 字段
                        if "modificationDateTime" not in thought and "modifiedAt" in thought:
                            thought["modificationDateTime"] = thought["modifiedAt"]
                        thoughts.append(thought)
                except:
                    pass
        
        added = 0
        updated = 0
        
        for thought in thoughts:
            thought_id = thought.get("id")
            name = thought.get("name")
            modified_at = thought.get("modificationDateTime")
            
            if not thought_id or not name:
                continue
            
            # 检查是否已存在 (增量同步检查)
            existing = db.get_card(thought_id)
            
            # 如果是增量同步且节点未修改，跳过
            if last_sync and modified_at and existing:
                if modified_at <= last_sync:
                    continue
            
            # 插入或更新
            db.upsert_card(
                thought_id=thought_id,
                name=name,
                tb_modified_at=modified_at
            )
            
            if existing:
                updated += 1
            else:
                added += 1
        
        # 更新同步时间
        db.set_meta("last_sync_time", datetime.now().isoformat())
        
        return {
            "success": True,
            "added": added,
            "updated": updated,
            "total_scanned": len(thoughts),
            "last_sync": datetime.now().isoformat()
        }
    
    def get_due_cards(self, limit: int = 20) -> List[Dict]:
        """
        获取今日到期的卡片
        
        Args:
            limit: 最大返回数量
        
        Returns:
            到期卡片列表
        """
        cards = db.get_due_cards(limit)
        
        # 为每张卡片添加预估间隔
        for card in cards:
            card["next_intervals"] = estimate_next_intervals(
                card["interval_days"],
                card["ease_factor"]
            )
        
        return cards
    
    def get_card_detail(self, thought_id: str) -> Optional[Dict]:
        """
        获取卡片详情，包含 TheBrain 笔记
        
        Args:
            thought_id: 节点 ID
        
        Returns:
            卡片详情
        """
        card = db.get_card(thought_id)
        if not card:
            return None
        
        # 从 TheBrain 获取笔记
        try:
            note = self.client.get_note(thought_id, "markdown")
            card["note"] = note.get("markdown", "") if note else ""
        except Exception as e:
            card["note"] = ""
            card["note_error"] = str(e)
        
        # 添加预估间隔
        card["next_intervals"] = estimate_next_intervals(
            card["interval_days"],
            card["ease_factor"]
        )
        
        return card
    
    def review(self, thought_id: str, quality: int) -> Dict:
        """
        提交复习结果
        
        Args:
            thought_id: 节点 ID
            quality: 评分 0-3 (Again/Hard/Good/Easy)
        
        Returns:
            更新后的卡片信息
        """
        card = db.get_card(thought_id)
        if not card:
            return {"success": False, "error": "卡片不存在"}
        
        # 记录之前的间隔
        interval_before = card["interval_days"]
        
        # 计算新的间隔
        result = calculate_next_review(
            quality=quality,
            current_interval=card["interval_days"],
            ease_factor=card["ease_factor"],
            state=card["state"]
        )
        
        # 确定新状态
        if result.graduated:
            new_state = "review"
        elif quality < 2:
            new_state = "learning"
        else:
            new_state = "review"
        
        # 更新卡片
        updated_card = db.update_card_after_review(
            thought_id=thought_id,
            interval_days=result.next_interval,
            ease_factor=result.new_ease,
            next_review=result.next_review,
            state=new_state
        )
        
        # 记录复习日志
        db.add_review_log(
            card_id=thought_id,
            quality=quality,
            interval_before=interval_before,
            interval_after=result.next_interval
        )
        
        return {
            "success": True,
            "card": updated_card,
            "quality_label": get_quality_label(quality),
            "interval_before": interval_before,
            "interval_after": result.next_interval,
            "next_review": result.next_review.isoformat()
        }
    
    def get_stats(self) -> Dict:
        """获取 SRS 统计信息"""
        stats = db.get_stats()
        stats["flashcard_tag_id"] = self._get_flashcard_tag_id()
        return stats
    
    def suspend(self, thought_id: str) -> Dict:
        """暂停卡片"""
        success = db.suspend_card(thought_id)
        return {
            "success": success,
            "message": "卡片已暂停" if success else "卡片不存在"
        }
    
    def unsuspend(self, thought_id: str) -> Dict:
        """恢复卡片"""
        success = db.unsuspend_card(thought_id)
        return {
            "success": success,
            "message": "卡片已恢复" if success else "卡片不存在"
        }
    
    def get_all_cards(self) -> List[Dict]:
        """获取所有卡片"""
        return db.get_all_cards()


# 单例服务
_service: Optional[SRSService] = None


def get_srs_service() -> SRSService:
    """获取 SRS 服务单例"""
    global _service
    if _service is None:
        _service = SRSService()
    return _service
