# SRS 间隔重复系统使用指南

## 概述

SRS (Spaced Repetition System) 是一个类似 Anki 的间隔重复系统，基于 SM-2 算法，帮助你高效记忆 TheBrain 中的知识节点。

## 快速开始

### 1. 在 TheBrain 中创建 FlashCard 标签

1. 打开 TheBrain 软件
2. 创建一个名为 `FlashCard` 的标签 (Tag)
3. 将你想要复习的节点添加此标签

### 2. 同步卡片

```bash
# API 方式
curl -X POST http://localhost:8000/api/srs/sync \
  -H "Authorization: Bearer YOUR_API_KEY"

# 强制全量同步
curl -X POST "http://localhost:8000/api/srs/sync?force_full=true" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 3. 获取今日待复习卡片

```bash
curl http://localhost:8000/api/srs/cards/due \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 4. 复习卡片

```bash
# quality: 0=Again, 1=Hard, 2=Good, 3=Easy
curl -X POST http://localhost:8000/api/srs/cards/{thought_id}/review \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"quality": 2}'
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/srs/sync` | POST | 同步 FlashCard 标签节点 |
| `/api/srs/cards/due` | GET | 获取今日到期卡片 |
| `/api/srs/cards/{id}` | GET | 获取卡片详情(含笔记) |
| `/api/srs/cards/{id}/review` | POST | 提交复习结果 |
| `/api/srs/cards/{id}/suspend` | POST | 暂停卡片 |
| `/api/srs/cards/{id}/unsuspend` | POST | 恢复卡片 |
| `/api/srs/cards` | GET | 获取所有卡片 |
| `/api/srs/stats` | GET | 获取学习统计 |

## MCP 工具

> 以下工具可在 AI 助手中使用

| 工具 | 说明 |
|------|------|
| `srs_sync` | 同步 FlashCard 标签节点 |
| `srs_get_due_cards` | 获取今日到期卡片 |
| `srs_get_card` | 获取单张卡片详情 |
| `srs_review` | 提交复习结果 |
| `srs_stats` | 获取学习统计 |
| `srs_suspend` | 暂停卡片 |
| `srs_unsuspend` | 恢复卡片 |

## 复习评分标准 (Anki 风格)

| 评分 | 名称 | 说明 | 效果 |
|------|------|------|------|
| 0 | Again | 完全忘记 | 间隔重置为 1 天，难度降低 |
| 1 | Hard | 记住但很困难 | 间隔稍微增加，难度略降 |
| 2 | Good | 正常记住 | 间隔按难度因子增加 |
| 3 | Easy | 轻松记住 | 间隔大幅增加，难度提高 |

## SM-2 算法

间隔计算公式：
- 新卡片第一次复习后：1 天
- 第二次 Good 后：3 天
- 之后：`当前间隔 × 难度因子`
- Easy 额外加成：×1.3

典型间隔序列：`1d → 3d → 7d → 17d → 42d → 100d...`

## 文件结构

```
srs/
├── __init__.py      # 模块初始化
├── algorithm.py     # SM-2 算法实现
├── db.py            # SQLite 数据库操作
├── service.py       # 服务层
├── srs.db           # SQLite 数据库文件
└── task_plan.md     # 开发任务计划
```

## 数据库

数据存储在 `srs/srs.db` SQLite 文件中，包含三张表：

1. **cards** - 卡片主表
   - thought_id, name, state, interval_days, ease_factor, next_review 等

2. **sync_meta** - 同步元数据
   - 存储 last_sync_time, flashcard_tag_id 等

3. **review_logs** - 复习历史
   - 记录每次复习的评分和间隔变化

## 常见问题

### Q: 同步失败提示"未找到 FlashCard 标签"
A: 请在 TheBrain 中创建一个名为 `FlashCard` 的标签（注意大小写）

### Q: 如何查看学习进度？
A: 调用 `/api/srs/stats` 获取统计信息

### Q: 如何暂时跳过某张卡片？
A: 使用 `suspend` 接口暂停卡片，之后可以用 `unsuspend` 恢复
