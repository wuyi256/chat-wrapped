"""把统计结果渲染成一份自包含的 HTML 年度报告（无外部依赖，可离线打开）。"""
from __future__ import annotations

import html
from typing import Dict, List, Sequence

_ACCENT = "#6366f1"
_ACCENT2 = "#8b5cf6"


def _bars_svg(values: Sequence[int], labels: Sequence[str], color: str = _ACCENT,
              width: int = 660, height: int = 190, label_every: int = 1) -> str:
    mx = max(values) if values else 0
    mx = mx or 1
    n = len(values)
    bw = width / n
    parts = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
             f'style="width:100%;height:auto">']
    for i, v in enumerate(values):
        bh = (height - 34) * v / mx
        x = i * bw + 1.5
        y = height - 22 - bh
        opacity = 0.35 + 0.65 * v / mx
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw - 3:.1f}" height="{max(bh, 1):.1f}" '
            f'rx="3" fill="{color}" opacity="{opacity:.2f}">'
            f"<title>{html.escape(str(labels[i]))}: {v}</title></rect>"
        )
        if i % label_every == 0:
            parts.append(
                f'<text x="{x + (bw - 3) / 2:.1f}" y="{height - 7}" text-anchor="middle" '
                f'font-size="10" fill="#6b7280">{html.escape(str(labels[i]))}</text>'
            )
    parts.append("</svg>")
    return "".join(parts)


def _sender_rows(participants: List[tuple]) -> str:
    mx = participants[0][1] if participants else 1
    rows = []
    for rank, (name, count) in enumerate(participants[:10], 1):
        pct = count / mx * 100
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"{rank}.")
        rows.append(
            f'<div class="rank-row"><span class="rank-name">{medal} {html.escape(name)}</span>'
            f'<div class="rank-track"><div class="rank-fill" style="width:{pct:.1f}%"></div></div>'
            f'<span class="rank-num">{count}</span></div>'
        )
    return "".join(rows)


def _emoji_grid(top_emojis: List[tuple]) -> str:
    if not top_emojis:
        return '<p class="muted">这一年你们一个表情都没发，狠人。</p>'
    cells = "".join(
        f'<div class="emoji-cell"><span class="emoji">{e}</span><span class="emoji-num">{c}</span></div>'
        for e, c in top_emojis
    )
    return f'<div class="emoji-grid">{cells}</div>'


def _word_rows(top_words: List[tuple]) -> str:
    if not top_words:
        return '<p class="muted">没提取到热词。</p>'
    mx = top_words[0][1] or 1
    rows = []
    for w, c in top_words:
        pct = c / mx * 100
        rows.append(
            f'<div class="rank-row"><span class="rank-name word">{html.escape(w)}</span>'
            f'<div class="rank-track"><div class="rank-fill" style="width:{pct:.1f}%"></div></div>'
            f'<span class="rank-num">{c}</span></div>'
        )
    return "".join(rows)


def render_html(stats: Dict, title: str = "年度聊天报告") -> str:
    month_labels = [f"{m}月" for m in range(1, 13)]
    hour_labels = [str(h) for h in range(24)]
    night_king, night_count = stats["late_night_king"]

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<style>
  :root {{ --bg:#f6f7fb; --card:#fff; --ink:#1f2430; --muted:#6b7280; --border:#e5e7eb; }}
  * {{ box-sizing:border-box; margin:0; padding:0 }}
  body {{ background:var(--bg); color:var(--ink);
         font-family:"PingFang SC","Microsoft YaHei",system-ui,sans-serif; line-height:1.7 }}
  .hero {{ background:linear-gradient(135deg,{_ACCENT},{_ACCENT2}); color:#fff;
           padding:56px 20px 44px; text-align:center }}
  .hero h1 {{ font-size:34px; letter-spacing:1px }}
  .hero p {{ opacity:.85; margin-top:8px; font-size:14px }}
  .wrap {{ max-width:760px; margin:-26px auto 60px; padding:0 16px }}
  .card {{ background:var(--card); border:1px solid var(--border); border-radius:14px;
           padding:22px 24px; margin-bottom:18px; box-shadow:0 2px 8px rgba(30,30,70,.06) }}
  .card h2 {{ font-size:18px; margin-bottom:14px }}
  .stat-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px }}
  .stat {{ background:#f4f5fb; border-radius:12px; padding:14px; text-align:center }}
  .stat .num {{ font-size:26px; font-weight:700; color:{_ACCENT} }}
  .stat .label {{ font-size:12px; color:var(--muted); margin-top:2px }}
  .rank-row {{ display:grid; grid-template-columns:110px 1fr 52px; gap:10px;
               align-items:center; margin:8px 0; font-size:14px }}
  .rank-name {{ white-space:nowrap; overflow:hidden; text-overflow:ellipsis }}
  .rank-name.word {{ font-weight:600 }}
  .rank-track {{ background:#eef0f6; border-radius:6px; height:12px; overflow:hidden }}
  .rank-fill {{ height:100%; border-radius:6px;
                background:linear-gradient(90deg,{_ACCENT},{_ACCENT2}) }}
  .rank-num {{ text-align:right; color:var(--muted); font-size:13px }}
  .emoji-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(88px,1fr)); gap:10px }}
  .emoji-cell {{ background:#f4f5fb; border-radius:12px; padding:12px 6px; text-align:center }}
  .emoji {{ font-size:26px; display:block }}
  .emoji-num {{ font-size:12px; color:var(--muted) }}
  .muted {{ color:var(--muted); font-size:14px }}
  .night {{ display:flex; align-items:baseline; gap:10px; flex-wrap:wrap }}
  .night .big {{ font-size:30px; font-weight:700; color:{_ACCENT2} }}
  footer {{ text-align:center; color:var(--muted); font-size:12px; padding-bottom:40px }}
  footer a {{ color:{_ACCENT}; text-decoration:none }}
</style>
</head>
<body>
<div class="hero">
  <h1>🎧 {html.escape(title)}</h1>
  <p>{stats["first_day"]} ~ {stats["last_day"]} · 数据全部在本地处理，聊天记录不出本机</p>
</div>
<div class="wrap">

  <div class="card">
    <div class="stat-grid">
      <div class="stat"><div class="num">{stats["total"]}</div><div class="label">总消息数</div></div>
      <div class="stat"><div class="num">{len(stats["participants"])}</div><div class="label">参与人数</div></div>
      <div class="stat"><div class="num">{stats["active_days"]}</div><div class="label">有聊天的天数</div></div>
      <div class="stat"><div class="num">{stats["longest_streak"]}</div><div class="label">最长连续聊天（天）</div></div>
    </div>
  </div>

  <div class="card">
    <h2>📅 哪个月最话痨</h2>
    {_bars_svg(stats["months"], month_labels, _ACCENT)}
  </div>

  <div class="card">
    <h2>⏰ 一天中的活跃时段</h2>
    {_bars_svg(stats["hours"], hour_labels, _ACCENT2, label_every=2)}
    <p class="muted">横轴是小时（0–23 点），柱子越高话越多。</p>
  </div>

  <div class="card">
    <h2>🌙 熬夜指数</h2>
    <div class="night">
      <span class="big">{stats["late_night_total"]}</span>
      <span>条消息是在凌晨 0–6 点发出的</span>
    </div>
    <p class="muted">熬夜冠军：{html.escape(str(night_king))}（{night_count} 条）——早点睡吧朋友。</p>
  </div>

  <div class="card">
    <h2>🗣️ 话痨榜</h2>
    {_sender_rows(stats["participants"])}
  </div>

  <div class="card">
    <h2>😂 年度表情 TOP {stats["topn"]}</h2>
    {_emoji_grid(stats["top_emojis"])}
  </div>

  <div class="card">
    <h2>🔥 年度热词 TOP {stats["topn"]}</h2>
    {_word_rows(stats["top_words"])}
  </div>

  <div class="card">
    <h2>🏆 最疯狂的一天</h2>
    <p><b>{stats["most_active_day"]}</b> 这一天你们发了 <b>{stats["most_active_count"]}</b> 条消息。那天发生什么了？</p>
  </div>

</div>
<footer>由 <a href="https://github.com/wuyi256/chat-wrapped">chat-wrapped</a> 生成</footer>
</body>
</html>"""
