"""
SM-2 间隔重复算法

基于 SuperMemo SM-2 算法的简化实现，用于计算下次复习时间。

评分标准 (Anki 风格):
- 0 = Again (完全忘记)
- 1 = Hard (记住但困难)
- 2 = Good (正常记住)
- 3 = Easy (轻松记住)
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Tuple


@dataclass
class ReviewResult:
    """复习结果"""
    next_interval: int      # 下次间隔(天)
    new_ease: float         # 新的难度因子
    next_review: date       # 下次复习日期
    graduated: bool         # 是否毕业(间隔超过 21 天)


# 默认参数
DEFAULT_EASE = 2.5
MIN_EASE = 1.3
GRADUATION_INTERVAL = 21  # 间隔超过 21 天视为毕业

# 新卡学习步骤 (分钟)
LEARNING_STEPS = [1, 10]  # 第一次 1 分钟后，第二次 10 分钟后


def calculate_next_review(
    quality: int,
    current_interval: int,
    ease_factor: float,
    state: str = "review"
) -> ReviewResult:
    """
    计算下次复习的间隔和日期
    
    Args:
        quality: 评分 0-3 (Again/Hard/Good/Easy)
        current_interval: 当前间隔(天)
        ease_factor: 当前难度因子
        state: 卡片状态 (new/learning/review)
    
    Returns:
        ReviewResult 包含新间隔、新难度、下次复习日期
    """
    today = date.today()
    
    # 限制 quality 范围
    quality = max(0, min(3, quality))
    
    # Again (质量 0): 重新学习
    if quality == 0:
        new_interval = 1
        new_ease = max(MIN_EASE, ease_factor - 0.2)
    
    # Hard (质量 1): 间隔稍微增加
    elif quality == 1:
        if current_interval == 0:
            new_interval = 1
        else:
            new_interval = max(1, int(current_interval * 1.2))
        new_ease = max(MIN_EASE, ease_factor - 0.15)
    
    # Good (质量 2): 正常增加间隔
    elif quality == 2:
        if current_interval == 0:
            new_interval = 1
        elif current_interval == 1:
            new_interval = 3
        else:
            new_interval = int(current_interval * ease_factor)
        new_ease = ease_factor
    
    # Easy (质量 3): 大幅增加间隔
    else:  # quality == 3
        if current_interval == 0:
            new_interval = 4
        elif current_interval == 1:
            new_interval = 4
        else:
            new_interval = int(current_interval * ease_factor * 1.3)
        new_ease = ease_factor + 0.15
    
    # 确保 ease 不低于最小值
    new_ease = max(MIN_EASE, new_ease)
    
    # 计算下次复习日期
    next_review = today + timedelta(days=new_interval)
    
    # 判断是否毕业
    graduated = new_interval >= GRADUATION_INTERVAL
    
    return ReviewResult(
        next_interval=new_interval,
        new_ease=round(new_ease, 2),
        next_review=next_review,
        graduated=graduated
    )


def get_quality_label(quality: int) -> str:
    """获取评分的文字标签"""
    labels = {
        0: "Again",
        1: "Hard",
        2: "Good",
        3: "Easy"
    }
    return labels.get(quality, "Unknown")


def estimate_next_intervals(
    current_interval: int,
    ease_factor: float
) -> dict:
    """
    预估不同评分下的下次间隔（用于展示给用户）
    
    Returns:
        {0: "1d", 1: "2d", 2: "5d", 3: "10d"} 格式的字典
    """
    result = {}
    for q in range(4):
        review = calculate_next_review(q, current_interval, ease_factor)
        days = review.next_interval
        if days == 1:
            result[q] = "1d"
        elif days < 30:
            result[q] = f"{days}d"
        elif days < 365:
            result[q] = f"{days // 30}mo"
        else:
            result[q] = f"{days // 365}y"
    return result
