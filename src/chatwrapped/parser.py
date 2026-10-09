"""微信导出 txt 聊天记录解析器（容错多格式）。

已支持两种常见的导出格式（其余变体通常也能被容错逻辑兜住）：

格式 A（昵称在前）：
    阿杰 2026-03-05 23:14:02
    今晚打球不

格式 B（日期在前）：
    2026/3/5 23:14:02 阿杰
    今晚打球不

规则：
- 匹配到头部行 = 开启一条新消息；其余行并入上一条消息的内容（多行消息）
- 消息之间用空行分隔（不强制，头部行本身就够判断）
- 系统消息（撤回、入群、拍一拍等）默认过滤
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

_HEADER_RES = [
    # 昵称 2026-03-05 23:14:02
    re.compile(
        r"^(?P<sender>\S.*?)\s+"
        r"(?P<y>\d{4})[-/](?P<mo>\d{1,2})[-/](?P<d>\d{1,2})\s+"
        r"(?P<h>\d{1,2}):(?P<mi>\d{1,2})(?::(?P<s>\d{1,2}))?\s*$"
    ),
    # 2026/3/5 23:14:02 昵称
    re.compile(
        r"^(?P<y>\d{4})[-/](?P<mo>\d{1,2})[-/](?P<d>\d{1,2})\s+"
        r"(?P<h>\d{1,2}):(?P<mi>\d{1,2})(?::(?P<s>\d{1,2}))?\s+"
        r"(?P<sender>.+?)\s*$"
    ),
]

_SYSTEM_HINTS = (
    "撤回了一条消息",
    "开启了朋友验证",
    "以上是打招呼的内容",
    "你已添加了",
    "加入了群聊",
    "退出了群聊",
    "修改群聊名称",
    "你被移出群聊",
)


@dataclass
class Message:
    dt: datetime
    sender: str
    content: str


def _match_header(line: str) -> Optional[dict]:
    for rx in _HEADER_RES:
        m = rx.match(line)
        if m:
            return m.groupdict()
    return None


def _to_datetime(g: dict) -> datetime:
    return datetime(
        int(g["y"]), int(g["mo"]), int(g["d"]),
        int(g["h"]), int(g["mi"]), int(g["s"] or 0),
    )


def is_system_message(content: str) -> bool:
    return any(hint in content for hint in _SYSTEM_HINTS)


def parse_chat(text: str, keep_system: bool = False) -> List[Message]:
    """把导出的聊天记录文本解析为消息列表（按时间排序）。"""
    messages: List[Message] = []
    cur_header: Optional[dict] = None
    cur_lines: List[str] = []

    def flush() -> None:
        nonlocal cur_header, cur_lines
        if cur_header is None:
            cur_lines = []
            return
        content = "\n".join(cur_lines).strip("\n")
        if content and (keep_system or not is_system_message(content)):
            messages.append(Message(_to_datetime(cur_header), cur_header["sender"].strip(), content))
        cur_header = None
        cur_lines = []

    for raw in text.splitlines():
        line = raw.rstrip()
        header = _match_header(line) if line.strip() else None
        if header is not None:
            flush()
            cur_header = header
        elif cur_header is not None:
            cur_lines.append(line)
        # 头部之前的行（文件说明等）直接忽略
    flush()

    messages.sort(key=lambda m: m.dt)
    return messages
