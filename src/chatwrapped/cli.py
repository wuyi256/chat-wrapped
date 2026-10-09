"""命令行入口：chatwrapped <聊天记录.txt> -o report.html；或 --demo 直接看演示。"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analyzer import analyze
from .parser import parse_chat
from .report import render_html


def _read_text(path: str) -> str:
    raw = Path(path).read_bytes()
    for enc in ("utf-8", "gb18030"):  # Windows 上微信导出经常是 GBK
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(
        prog="chatwrapped",
        description="聊天记录年度总结：把微信导出的 txt 变成一份 HTML 年度报告。",
    )
    parser.add_argument("file", nargs="?", help="微信导出的聊天记录 txt")
    parser.add_argument("-o", "--output", default="chat-report.html", help="输出 HTML 路径")
    parser.add_argument("--title", default="年度聊天报告", help="报告标题")
    parser.add_argument("--top", type=int, default=10, help="热词/表情榜单长度")
    parser.add_argument("--demo", action="store_true", help="用内置演示数据生成一份报告")
    parser.add_argument("--keep-system", action="store_true", help="保留撤回/入群等系统消息")
    args = parser.parse_args(argv)

    if args.demo:
        from .demo import make_demo_messages

        messages = make_demo_messages()
        print(f"[demo] 已生成 {len(messages)} 条演示消息")
    else:
        if not args.file:
            parser.error("请提供聊天记录文件，或使用 --demo 生成演示报告")
        text = _read_text(args.file)
        messages = parse_chat(text, keep_system=args.keep_system)
        if not messages:
            print("没有解析到任何消息。请检查文件格式（支持「昵称 日期 时间」或「日期 时间 昵称」两种头部）。",
                  file=sys.stderr)
            return 2

    stats = analyze(messages, topn=args.top)
    html_text = render_html(stats, title=args.title)
    Path(args.output).write_text(html_text, encoding="utf-8")

    print(f"解析到 {stats['total']} 条消息，{len(stats['participants'])} 位参与者")
    print(f"时间跨度：{stats['first_day']} ~ {stats['last_day']}")
    print(f"报告已生成：{args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
