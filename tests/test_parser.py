# -*- coding: utf-8 -*-
import unittest

from chatwrapped import analyze, parse_chat
from chatwrapped.demo import make_demo_messages

FORMAT_A = """阿杰 2026-03-05 23:14:02
今晚打球不

我 2026/3/5 23:15:10
来，老地方
带瓶水

阿杰 2026-03-05 23:16:00
行
"""

FORMAT_B = """2026-03-05 23:14:02 阿杰
今晚打球不

2026/3/5 23:15:10 我
来，老地方
"""

WITH_SYSTEM = """阿杰 2026-03-05 23:14:02
在吗

我 2026-03-05 23:15:10
你撤回了一条消息

我 2026-03-05 23:16:00
发错了
"""


class TestParser(unittest.TestCase):
    def test_format_a(self):
        msgs = parse_chat(FORMAT_A)
        self.assertEqual(len(msgs), 3)
        self.assertEqual(msgs[0].sender, "阿杰")
        self.assertEqual(msgs[1].content, "来，老地方\n带瓶水")  # 多行合并
        self.assertEqual(msgs[1].dt.hour, 23)

    def test_format_b(self):
        msgs = parse_chat(FORMAT_B)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0].content, "今晚打球不")

    def test_system_message_filtered(self):
        msgs = parse_chat(WITH_SYSTEM)
        self.assertEqual(len(msgs), 2)
        self.assertNotIn("撤回", "".join(m.content for m in msgs))

    def test_keep_system(self):
        msgs = parse_chat(WITH_SYSTEM, keep_system=True)
        self.assertEqual(len(msgs), 3)

    def test_sorted_by_time(self):
        msgs = parse_chat(FORMAT_A)
        times = [m.dt for m in msgs]
        self.assertEqual(times, sorted(times))


class TestAnalyzer(unittest.TestCase):
    def test_basic_counts(self):
        msgs = parse_chat(FORMAT_A)
        stats = analyze(msgs)
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["hours"][23], 3)      # 三条都在 23 点
        self.assertEqual(stats["months"][2], 3)      # 都在三月
        self.assertEqual(stats["late_night_total"], 0)
        senders = dict(stats["participants"])
        self.assertEqual(senders["阿杰"], 2)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            analyze([])

    def test_demo_deterministic(self):
        a = make_demo_messages(seed=1, n=50)
        b = make_demo_messages(seed=1, n=50)
        self.assertEqual([m.content for m in a], [m.content for m in b])
        stats = analyze(a)
        self.assertEqual(stats["total"], 50)
        self.assertTrue(all(m.dt.year == 2026 for m in a))


if __name__ == "__main__":
    unittest.main()
