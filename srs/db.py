"""
SRS 数据库模块

使用 SQLite 存储卡片信息和复习调度数据。
"""

import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from contextlib import contextmanager


# 数据库文件路径
DB_PATH = Path(__file__).parent / "srs.db"


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # 支持字典式访问
    return conn


@contextmanager
def get_db():
    """数据库连接上下文管理器"""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """初始化数据库表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 卡片主表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                thought_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                state TEXT DEFAULT 'new',
                interval_days INTEGER DEFAULT 0,
                ease_factor REAL DEFAULT 2.5,
                review_count INTEGER DEFAULT 0,
                next_review DATE,
                last_review DATETIME,
                tb_modified_at TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 同步元数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # 复习历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id TEXT,
                quality INTEGER,
                interval_before INTEGER,
                interval_after INTEGER,
                reviewed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_next_review ON cards(next_review)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_state ON cards(state)
        """)


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """将 Row 对象转换为字典"""
    if row is None:
        return None
    return dict(row)


# ========== Cards CRUD ==========

def get_card(thought_id: str) -> Optional[Dict]:
    """获取单张卡片"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cards WHERE thought_id = ?", (thought_id,))
        return row_to_dict(cursor.fetchone())


def get_all_cards() -> List[Dict]:
    """获取所有卡片"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cards ORDER BY next_review")
        return [row_to_dict(row) for row in cursor.fetchall()]


def get_due_cards(limit: int = 20) -> List[Dict]:
    """获取今日到期的卡片"""
    today = date.today().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM cards 
            WHERE (next_review IS NULL OR next_review <= ?) 
              AND state != 'suspended'
            ORDER BY 
                CASE state 
                    WHEN 'new' THEN 0 
                    WHEN 'learning' THEN 1 
                    ELSE 2 
                END,
                next_review
            LIMIT ?
        """, (today, limit))
        return [row_to_dict(row) for row in cursor.fetchall()]


def upsert_card(
    thought_id: str,
    name: str,
    tb_modified_at: str = None,
    **kwargs
) -> Dict:
    """插入或更新卡片"""
    existing = get_card(thought_id)
    now = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        if existing:
            # 更新现有卡片 (只更新名称和修改时间，不改变 SRS 状态)
            cursor.execute("""
                UPDATE cards 
                SET name = ?, tb_modified_at = ?, updated_at = ?
                WHERE thought_id = ?
            """, (name, tb_modified_at, now, thought_id))
        else:
            # 插入新卡片
            cursor.execute("""
                INSERT INTO cards (thought_id, name, state, interval_days, 
                                   ease_factor, review_count, next_review,
                                   tb_modified_at, created_at, updated_at)
                VALUES (?, ?, 'new', 0, 2.5, 0, ?, ?, ?, ?)
            """, (thought_id, name, date.today().isoformat(), 
                  tb_modified_at, now, now))
    
    # 在 with 块外重新获取卡片以确保数据已提交
    return get_card(thought_id)


def update_card_after_review(
    thought_id: str,
    interval_days: int,
    ease_factor: float,
    next_review: date,
    state: str = "review"
) -> Dict:
    """复习后更新卡片"""
    now = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cards 
            SET interval_days = ?,
                ease_factor = ?,
                next_review = ?,
                last_review = ?,
                review_count = review_count + 1,
                state = ?,
                updated_at = ?
            WHERE thought_id = ?
        """, (interval_days, ease_factor, next_review.isoformat(),
              now, state, now, thought_id))
        
        return get_card(thought_id)


def suspend_card(thought_id: str) -> bool:
    """暂停卡片"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cards SET state = 'suspended', updated_at = ?
            WHERE thought_id = ?
        """, (datetime.now().isoformat(), thought_id))
        return cursor.rowcount > 0


def unsuspend_card(thought_id: str) -> bool:
    """恢复卡片"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cards SET state = 'review', updated_at = ?
            WHERE thought_id = ?
        """, (datetime.now().isoformat(), thought_id))
        return cursor.rowcount > 0


def delete_card(thought_id: str) -> bool:
    """删除卡片"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cards WHERE thought_id = ?", (thought_id,))
        return cursor.rowcount > 0


# ========== Sync Meta ==========

def get_meta(key: str) -> Optional[str]:
    """获取同步元数据"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM sync_meta WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else None


def set_meta(key: str, value: str):
    """设置同步元数据"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sync_meta (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = ?
        """, (key, value, value))


# ========== Review Logs ==========

def add_review_log(
    card_id: str, 
    quality: int, 
    interval_before: int, 
    interval_after: int
):
    """添加复习日志"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO review_logs (card_id, quality, interval_before, interval_after)
            VALUES (?, ?, ?, ?)
        """, (card_id, quality, interval_before, interval_after))


# ========== Statistics ==========

def get_stats() -> Dict:
    """获取统计信息"""
    today = date.today().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 总卡片数
        cursor.execute("SELECT COUNT(*) as total FROM cards")
        total = cursor.fetchone()["total"]
        
        # 各状态数量
        cursor.execute("""
            SELECT state, COUNT(*) as count FROM cards GROUP BY state
        """)
        states = {row["state"]: row["count"] for row in cursor.fetchall()}
        
        # 今日到期
        cursor.execute("""
            SELECT COUNT(*) as due FROM cards 
            WHERE (next_review IS NULL OR next_review <= ?) AND state != 'suspended'
        """, (today,))
        due_today = cursor.fetchone()["due"]
        
        # 今日已复习
        cursor.execute("""
            SELECT COUNT(*) as reviewed FROM review_logs 
            WHERE date(reviewed_at) = ?
        """, (today,))
        reviewed_today = cursor.fetchone()["reviewed"]
        
        return {
            "total_cards": total,
            "new": states.get("new", 0),
            "learning": states.get("learning", 0),
            "review": states.get("review", 0),
            "suspended": states.get("suspended", 0),
            "due_today": due_today,
            "reviewed_today": reviewed_today
        }


# 初始化数据库
init_db()
