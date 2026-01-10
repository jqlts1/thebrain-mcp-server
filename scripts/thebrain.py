import sys
import argparse
import requests
from client import TheBrainClient

def output(data):
    """输出 JSON 结果"""
    import json
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(prog="thebrain", description="TheBrain CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # search
    p = sub.add_parser("search", help="搜索想法")
    p.add_argument("query", help="搜索关键词")
    p.add_argument("-n", "--max", type=int, default=30, help="最大结果数")

    # get
    p = sub.add_parser("get", help="获取想法详情")
    p.add_argument("id", help="想法ID")

    # graph
    p = sub.add_parser("graph", help="获取想法图谱")
    p.add_argument("id", help="想法ID")
    p.add_argument("--siblings", action="store_true", help="包含兄弟想法")

    # children
    p = sub.add_parser("children", help="获取子想法")
    p.add_argument("id", help="想法ID")

    # parents
    p = sub.add_parser("parents", help="获取父想法")
    p.add_argument("id", help="想法ID")

    # jumps
    p = sub.add_parser("jumps", help="获取跳转链接")
    p.add_argument("id", help="想法ID")

    # create
    p = sub.add_parser("create", help="创建想法")
    p.add_argument("name", help="想法名称")
    p.add_argument("--parent", help="父想法ID")
    p.add_argument("--jump", help="跳转链接目标ID")
    p.add_argument("--kind", type=int, default=1, help="类型: 1=普通 2=类型 4=标签")

    # update
    p = sub.add_parser("update", help="更新想法")
    p.add_argument("id", help="想法ID")
    p.add_argument("--name", help="新名称")
    p.add_argument("--label", help="新标签")
    p.add_argument("--color", help="前景色 如 #ff7145")
    p.add_argument("--type", dest="type_id", help="类型ID")

    # delete
    p = sub.add_parser("delete", help="删除想法")
    p.add_argument("id", help="想法ID")

    # link
    p = sub.add_parser("link", help="创建链接")
    p.add_argument("id_a", help="起始想法ID")
    p.add_argument("id_b", help="目标想法ID")
    p.add_argument("--relation", type=int, default=3, help="关系: 1=子 2=父 3=跳转")
    p.add_argument("--name", help="链接标签")

    # unlink
    p = sub.add_parser("unlink", help="删除链接")
    p.add_argument("link_id", help="链接ID")

    # note
    p = sub.add_parser("note", help="操作笔记")
    p.add_argument("id", help="想法ID")
    p.add_argument("--set", dest="content", help="设置笔记内容")
    p.add_argument("--append", dest="append_content", help="追加内容")
    p.add_argument("--format", default="markdown", choices=["markdown", "html", "text"])

    # types
    sub.add_parser("types", help="列出所有类型")

    # tags
    sub.add_parser("tags", help="列出所有标签")

    # pins
    sub.add_parser("pins", help="列出置顶想法")

    # attachments
    p = sub.add_parser("attachments", help="获取附件")
    p.add_argument("id", help="想法ID")

    # add-url
    p = sub.add_parser("add-url", help="添加URL附件")
    p.add_argument("id", help="想法ID")
    p.add_argument("url", help="URL地址")
    p.add_argument("--name", help="附件名称")

    args = parser.parse_args()

    try:
        client = TheBrainClient()

        if args.cmd == "search":
            output(client.search(args.query, args.max))

        elif args.cmd == "get":
            output(client.get_thought(args.id))

        elif args.cmd == "graph":
            output(client.get_graph(args.id, args.siblings))

        elif args.cmd == "children":
            output(client.get_children(args.id))

        elif args.cmd == "parents":
            output(client.get_parents(args.id))

        elif args.cmd == "jumps":
            output(client.get_jumps(args.id))

        elif args.cmd == "create":
            if args.parent:
                result = client.create_thought(args.name, args.parent, 1, args.kind)
            elif args.jump:
                result = client.create_thought(args.name, args.jump, 3, args.kind)
            else:
                result = client.create_thought(args.name, kind=args.kind)
            output(result)

        elif args.cmd == "update":
            updates = []
            if args.name:
                updates.append({"op": "replace", "path": "/name", "value": args.name})
            if args.label:
                updates.append({"op": "replace", "path": "/label", "value": args.label})
            if args.color:
                updates.append({"op": "replace", "path": "/foregroundColor", "value": args.color})
            if args.type_id:
                updates.append({"op": "replace", "path": "/typeId", "value": args.type_id})
            if updates:
                client.update_thought(args.id, updates)
                output({"status": "ok"})
            else:
                print("错误: 请指定要更新的属性", file=sys.stderr)
                sys.exit(1)

        elif args.cmd == "delete":
            client.delete_thought(args.id)
            output({"status": "ok"})

        elif args.cmd == "link":
            output(client.create_link(args.id_a, args.id_b, args.relation, args.name))

        elif args.cmd == "unlink":
            client.delete_link(args.link_id)
            output({"status": "ok"})

        elif args.cmd == "note":
            if args.content:
                client.update_note(args.id, args.content)
                output({"status": "ok"})
            elif args.append_content:
                client.append_note(args.id, args.append_content)
                output({"status": "ok"})
            else:
                output(client.get_note(args.id, args.format))

        elif args.cmd == "types":
            output(client.get_types())

        elif args.cmd == "tags":
            output(client.get_tags())

        elif args.cmd == "pins":
            output(client.get_pins())

        elif args.cmd == "attachments":
            output(client.get_attachments(args.id))

        elif args.cmd == "add-url":
            output(client.add_url(args.id, args.url, args.name))

    except requests.HTTPError as e:
        print(f"API错误: {e.response.status_code} {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
