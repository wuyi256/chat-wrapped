"""统计分析：谁话最多、什么时候最活跃、年度热词、熬夜指数……"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import timedelta
from typing import Dict, List, Sequence

from .parser import Message

try:  # 装了 jieba 热词更准；没装自动退化 bigram
    import jieba  # type: ignore
except Exception:  # pragma: no cover
    jieba = None

_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]"
)
_CJK_RUN_RE = re.compile(r"[一-鿿]{2,}")

_STOPWORDS = {
    "我们", "你们", "他们", "她们", "自己", "这个", "那个", "这些", "那些", "就是",
    "不是", "没有", "什么", "怎么", "怎样", "这样", "那样", "可以", "还是", "现在",
    "知道", "真的", "觉得", "感觉", "可能", "应该", "因为", "所以", "但是", "然后",
    "已经", "一个", "一些", "一下", "的时候", "为什么", "这么", "那么", "如果",
    "的话", "哈哈", "哈哈哈", "哈哈哈哈", "呵呵", "嘿嘿", "嗯嗯", "哦哦",
    "图片", "表情", "视频", "链接",
}


def _top_words(messages: Sequence[Message], topn: int) -> List[tuple]:
    text = "\n".join(m.content for m in messages)
    counter: Counter = Counter()
    if jieba is not None:
        for w in jieba.cut(text):
            w = w.strip()
            if len(w) >= 2 and _CJK_RUN_RE.fullmatch(w) and w not in _STOPWORDS:
                counter[w] += 1
    else:
        for run in _CJK_RUN_RE.findall(text):
            for i in range(len(run) - 1):
                gram = run[i : i + 2]
                if gram not in _STOPWORDS:
                    counter[gram] += 1
    return counter.most_common(topn)


def _longest_streak(days: set) -> int:
    if not days:
        return 0
    best = cur = 1
    ordered = sorted(days)
    for prev, day in zip(ordered, ordered[1:]):
        cur = cur + 1 if day - prev == timedelta(days=1) else 1
        best = max(best, cur)
    return best


def analyze(messages: Sequence[Message], topn: int = 10) -> Dict:
    if not messages:
        raise ValueError("没有解析到任何消息")

    per_sender: Counter = Counter(m.sender for m in messages)
    months = [0] * 12
    hours = [0] * 24
    late_night: Counter = Counter()
    emoji: Counter = Counter()
    per_day: Counter = Counter()
    days = set()

    for m in messages:
        months[m.dt.month - 1] += 1
        hours[m.dt.hour] += 1
        if m.dt.hour < 6:
            late_night[m.sender] += 1
        emoji.update(_EMOJI_RE.findall(m.content))
        day = m.dt.date()
        per_day[day] += 1
        days.add(day)

    most_active_day, most_active_count = per_day.most_common(1)[0]

    return {
        "total": len(messages),
        "participants": per_sender.most_common(),
        "months": months,
        "hours": hours,
        "late_night_total": sum(late_night.values()),
        "late_night_king": late_night.most_common(1)[0] if late_night else ("无", 0),
        "top_emojis": emoji.most_common(topn),
        "top_words": _top_words(messages, topn),
        "longest_streak": _longest_streak(days),
        "most_active_day": most_active_day.isoformat(),
        "most_active_count": most_active_count,
        "first_day": min(days).isoformat(),
        "last_day": max(days).isoformat(),
        "active_days": len(days),
        "topn": topn,
    }
