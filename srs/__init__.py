"""
TheBrain SRS (Spaced Repetition System) 模块

提供类似 Anki 的间隔重复功能，支持从 TheBrain 同步带 FlashCard 标签的节点。
"""

from .service import SRSService

__all__ = ['SRSService']
