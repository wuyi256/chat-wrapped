# chat-wrapped · 聊天记录年度总结

把微信导出的聊天记录（txt）变成一份**「网易云年度歌单」式的 HTML 报告**：谁话最多、你们几点最活跃、熬夜冠军是谁、年度表情和热词是什么。

**隐私优先**：全部计算在本机完成，生成的报告也是纯本地 HTML（零外部依赖，可离线打开），聊天记录不出你的电脑。

## 报告里有什么

- 📊 总消息数 / 参与人数 / 活跃天数 / 最长连续聊天纪录
- 📅 逐月活跃柱状图、24 小时活跃分布图（纯手写 SVG，无第三方库）
- 🌙 熬夜指数（凌晨 0–6 点的消息数 + 熬夜冠军）
- 🗣️ 话痨榜、😂 年度表情 TOP10、🔥 年度热词 TOP10
- 🏆 最疯狂的一天（单日消息数峰值）

## 快速开始

```bash
# 没有真实数据？先跑个演示看看效果
python -m chatwrapped --demo -o demo.html        # 需 PYTHONPATH=src，或先 pip install -e .

# 分析真实记录
chatwrapped 微信聊天记录.txt -o my-2026.html --title "我们的 2026"
```

Windows 微信导出的文件经常是 GBK 编码，工具会自动尝试 UTF-8 / GB18030 两种解码，不用自己转码。

## 支持的导出格式

两种常见的 txt 导出格式（自动识别）：

```
阿杰 2026-03-05 23:14:02          # 格式 A：昵称在前
今晚打球不

2026/3/5 23:15:10 我              # 格式 B：日期在前
来，老地方
```

- 多行消息自动合并
- 撤回、入群、打招呼等系统消息默认过滤（`--keep-system` 可保留）

## 热词提取

- 安装了 `jieba`：用分词提取热词（推荐，`pip install -e .[better-words]`）
- 没有 `jieba`：自动退化为中文 bigram 统计，零依赖也能跑

内置停用词表会过滤「我们、就是、哈哈」这类高频但无信息的词。

## 作为库调用

```python
from chatwrapped import parse_chat, analyze
from chatwrapped.report import render_html

messages = parse_chat(open("记录.txt", encoding="utf-8").read())
stats = analyze(messages)
open("report.html", "w", encoding="utf-8").write(render_html(stats, "我们的 2026"))
```

## 测试

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## License

MIT
