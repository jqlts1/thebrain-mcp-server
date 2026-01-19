# Task Plan: TheBrain SRS 间隔重复系统 MVP

## Goal
为 TheBrain 打造类似 Anki 的间隔重复系统，支持从 TheBrain 同步带 `FlashCard` 标签的节点，并实现 SM-2 算法进行复习调度。

## Phases
- [x] Phase 1: 数据库设计与初始化 ✅
- [x] Phase 2: 同步功能 (srs_sync) ✅
- [x] Phase 3: 获取到期卡片 (srs_get_due_cards) ✅
- [x] Phase 4: 复习提交 (srs_review) ✅
- [x] Phase 5: 集成到 API Server 和 MCP Server ✅
- [x] Phase 6: 测试与验证 ✅

## Key Questions
1. FlashCard 标签的 tag_id 如何获取？→ 通过 `list_metadata('tags')` 获取
2. 如何处理 TheBrain 中被删除的节点？→ 同步时标记为 suspended
3. 复习评分采用什么标准？→ Anki 风格 (Again=0, Hard=1, Good=2, Easy=3)

## Technical Design

### 文件结构
```
srs/
├── __init__.py      # 模块初始化
├── db.py            # SQLite 数据库操作
├── algorithm.py     # SM-2 间隔重复算法
├── service.py       # SRS 服务层
└── srs.db           # SQLite 数据库文件 (运行时生成)
```

### 数据库 Schema
```sql
CREATE TABLE cards (
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
);

CREATE TABLE sync_meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE review_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id TEXT,
    quality INTEGER,
    interval_before INTEGER,
    interval_after INTEGER,
    reviewed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### SM-2 算法核心
```python
def calculate_next_review(quality: int, interval: int, ease: float):
    if quality < 2:  # Again or Hard
        return 1, max(1.3, ease - 0.2)
    else:  # Good or Easy
        new_interval = interval * ease if interval > 0 else 1
        if quality == 3:  # Easy
            new_interval *= 1.3
        new_ease = ease + (0.1 - (3 - quality) * 0.08)
        return round(new_interval), max(1.3, new_ease)
```

## Decisions Made
- [SQLite]: 轻量级，无需额外服务，Python 内置支持
- [FlashCard 标签]: 用户手动标记，系统自动同步
- [增量同步]: 使用 modificationDateTime 过滤新增/修改的节点

## Errors Encountered
(空)

## Status
**Currently in Phase 1** - 创建数据库模块和初始化逻辑
