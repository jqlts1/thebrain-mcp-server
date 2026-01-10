---
name: thebrain
description: 操作和查询TheBrain知识图谱。支持：(1)搜索想法 (2)查看想法详情及父/子/跳转链接 (3)创建/更新/删除想法 (4)管理链接关系 (5)附件操作 (6)笔记读写 (7)类型和标签管理。适用于需要与TheBrain进行交互的任务，如知识管理、信息查询、图谱分析等。
---

# TheBrain CLI

CLI 工具路径: `scripts/thebrain.py`

环境配置 (.env):
```
THEBRAIN_API_KEY=your-api-key
THEBRAIN_BRAIN_ID=your-brain-id
```

## 命令速查

```bash
# 搜索
python thebrain.py search "关键词"
python thebrain.py search "Python" -n 10

# 获取想法
python thebrain.py get <id>
python thebrain.py graph <id>
python thebrain.py graph <id> --siblings

# 获取关联
python thebrain.py children <id>
python thebrain.py parents <id>
python thebrain.py jumps <id>

# 创建想法
python thebrain.py create "名称"
python thebrain.py create "子想法" --parent <parent_id>
python thebrain.py create "跳转目标" --jump <other_id>
python thebrain.py create "新标签" --kind 4

# 更新想法
python thebrain.py update <id> --name "新名称"
python thebrain.py update <id> --label "标签" --color "#ff7145"
python thebrain.py update <id> --type <type_id>

# 删除想法
python thebrain.py delete <id>

# 链接操作
python thebrain.py link <id_a> <id_b>                    # 跳转链接
python thebrain.py link <id_a> <id_b> --relation 1      # 子链接
python thebrain.py link <id_a> <id_b> --name "标签"
python thebrain.py unlink <link_id>

# 笔记操作
python thebrain.py note <id>                    # 获取笔记
python thebrain.py note <id> --format html
python thebrain.py note <id> --set "新内容"     # 替换笔记
python thebrain.py note <id> --append "追加"    # 追加内容

# 列表查询
python thebrain.py types       # 所有类型
python thebrain.py tags        # 所有标签
python thebrain.py pins        # 置顶想法

# 附件
python thebrain.py attachments <id>
python thebrain.py add-url <id> "https://..." --name "链接名"
```

## 关系类型

| 值 | 说明 |
|---|------|
| 1 | 子想法 (Child) |
| 2 | 父想法 (Parent) |
| 3 | 跳转链接 (Jump) |

## Kind 类型

| 值 | 说明 |
|---|------|
| 1 | 普通想法 |
| 2 | 类型定义 |
| 4 | 标签 |

## API 参考

详见 [references/api-reference.md](references/api-reference.md)
