"""演示数据生成器：没有真实聊天记录也能立刻看到报告效果。"""
from __future__ import annotations

import random
from datetime import date, datetime, time, timedelta
from typing import List

from .parser import Message

PARTICIPANTS = ["我", "阿杰", "小雨", "老王"]
_SENDER_WEIGHTS = [0.42, 0.24, 0.20, 0.14]

# 24 小时的活跃权重：深夜低、午休小高峰、晚上大高峰
_HOUR_WEIGHTS = [
    0.4, 0.2, 0.1, 0.05, 0.05, 0.1,      # 0-5  熬夜区
    0.3, 0.8, 1.5, 1.2, 1.0, 1.0,        # 6-11 上午
    1.6, 1.4, 0.8, 0.9, 1.0, 1.1,        # 12-17 下午
    1.5, 1.9, 2.4, 2.8, 2.5, 1.8,        # 18-23 晚上
]

_CHATTER = [
    "在吗", "今晚打球不 🏀", "食堂三楼的麻辣烫 yyds", "作业写完了吗",
    "哈哈哈哈哈哈", "刚睡醒", "考试周要死了 😭", "开黑吗", "帮我带杯奶茶",
    "明天早八，寄", "老师今天划重点了", "周末去爬山不", "这个表情包笑死 😂",
    "在宿舍吗", "帮我拿个快递呗", "晚饭吃啥", "图书馆还有座吗",
    "这题你会吗", "明天交报告别忘了", "新出的那部剧看了没", "宿舍没水了",
    "谁有充电宝", "今天好困 😴", "这课也太难了", "老师点名了吗",
    "我马上到", "等我五分钟", "冲冲冲", "可以可以", "牛的 👍",
    "绝了", "笑死", "绷不住了", "真的假的", "我裂开了",
    "晚上吃什么，选择困难了", "这个瓜你们吃了吗", "周末回家吗",
    "新生杯咱们报名不", "体测要来了，慌", "宿舍楼下又有猫了",
    "[图片]", "[视频]", "[表情]", "👍", "😂", "🥳", "❤️", "😭",
    "晚安晚安", "起不来，帮我答个到", "这门课绩点怎么算", "奖学金名单出了",
    "暑假实习找到了吗", "这个讲座要去吗", "组队打比赛吗", "保研夏令营开始了",
]


def make_demo_messages(seed: int = 42, n: int = 1200, year: int = 2026) -> List[Message]:
    """生成 n 条看起来像真的一样的演示消息，覆盖 year 年 1 月到 10 月。"""
    rnd = random.Random(seed)
    start = date(year, 1, 1)
    end = date(year, 10, 9)
    span = (end - start).days

    messages: List[Message] = []
    for _ in range(n):
        day = start + timedelta(days=rnd.randint(0, span))
        hour = rnd.choices(range(24), weights=_HOUR_WEIGHTS, k=1)[0]
        minute = rnd.randint(0, 59)
        second = rnd.randint(0, 59)
        sender = rnd.choices(PARTICIPANTS, weights=_SENDER_WEIGHTS, k=1)[0]
        content = rnd.choice(_CHATTER)
        if rnd.random() < 0.18:  # 偶尔连发 / 带表情后缀
            content += " " + rnd.choice(["😂", "😂😂", "👍", "🥳", rnd.choice(_CHATTER)])
        messages.append(Message(datetime.combine(day, time(hour, minute, second)), sender, content))

    messages.sort(key=lambda m: m.dt)
    return messages
