#!/usr/bin/env python3
"""Regenerate dashboard/index.html from tracks/*/progress.json and cards.jsonl.

Run from anywhere: python3 ~/learning/tools/gen_dashboard.py
No dependencies beyond the standard library. Missing or malformed files are
skipped with a warning, never fatal.
"""
import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKS = ROOT / "tracks"
OUT = ROOT / "dashboard" / "index.html"

STATUS = {
    "not_started": ("未开始", "#e2e7e5"),
    "in_progress": ("进行中", "#7fb8ae"),
    "gate_pending": ("待过门", "#e0a94f"),
    "mastered": ("已掌握", "#14665a"),
    "exempt": ("免修", "#9fc5bd"),
    "paused": ("维持", "#c3cbc8"),
}


def load_tracks():
    tracks = []
    if not TRACKS.is_dir():
        return tracks
    for d in sorted(TRACKS.iterdir()):
        pj = d / "progress.json"
        if not d.is_dir() or not pj.is_file():
            continue
        try:
            data = json.loads(pj.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"warn: skipping {pj}: {e}", file=sys.stderr)
            continue
        data["due_cards"] = count_due(d / "cards.jsonl")
        tracks.append(data)
    return tracks


def count_due(cards_path):
    due = total = 0
    if not cards_path.is_file():
        return 0
    today = date.today()
    for line in cards_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            card = json.loads(line)
            total += 1
            last = datetime.strptime(card["last_review"], "%Y-%m-%d").date()
            if (today - last).days >= card.get("stability_days", 1):
                due += 1
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
    return due


def module_strip(modules):
    cells = []
    for m in modules:
        label, color = STATUS.get(m.get("status", "not_started"), STATUS["not_started"])
        cells.append(
            f'<span class="mod" style="background:{color}" '
            f'title="{m.get("name", "?")} · {label}"></span>'
        )
    return "".join(cells)


def calibration_svg(points):
    """predicted vs actual, last 10 entries, as a tiny paired-dot chart."""
    pts = [p for p in points if isinstance(p.get("predicted"), (int, float))][-10:]
    if not pts:
        return '<p class="empty">尚无校准数据</p>'
    w, h, pad = 320, 90, 14
    step = (w - 2 * pad) / max(len(pts) - 1, 1)
    def y(v):
        return h - pad - (v / 100) * (h - 2 * pad)
    rows = []
    for i, p in enumerate(pts):
        x = pad + i * step
        rows.append(
            f'<line x1="{x:.0f}" y1="{y(p["predicted"]):.0f}" x2="{x:.0f}" y2="{y(p["actual"]):.0f}" stroke="#c3cbc8"/>'
            f'<circle cx="{x:.0f}" cy="{y(p["predicted"]):.0f}" r="3.5" fill="none" stroke="#77828d"/>'
            f'<circle cx="{x:.0f}" cy="{y(p["actual"]):.0f}" r="3.5" fill="#14665a"/>'
        )
    return (
        f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
        f'aria-label="预测（空心）vs 实测（实心）">{"".join(rows)}</svg>'
        '<p class="legend">空心=预测 · 实心=实测（最近 10 次）</p>'
    )


def render(tracks):
    today = date.today().isoformat()
    total_due = sum(t["due_cards"] for t in tracks)
    body = []
    if not tracks:
        body.append(
            '<div class="card empty-state"><h2>还没有开学的科目</h2>'
            "<p>对家教说「我想学 X」即可开始。这里会出现模块掌握地图、"
            "到期卡片和校准曲线。</p></div>"
        )
    for t in tracks:
        mastered = sum(1 for m in t.get("modules", []) if m.get("status") in ("mastered", "exempt"))
        body.append(f"""
  <div class="card">
    <div class="head">
      <h2>{t.get("title", t.get("track", "?"))}</h2>
      <span class="pill {t.get("status", "active")}">{t.get("mode", "")}</span>
    </div>
    <p class="stats">
      模块 {mastered}/{len(t.get("modules", []))} 掌握 ·
      到期卡片 <b>{t["due_cards"]}</b> ·
      会话 {t.get("total_sessions", 0)} 次 · 累计 {t.get("total_minutes", 0)} 分钟 ·
      上次 {t.get("last_session", "—")}
    </p>
    <div class="strip">{module_strip(t.get("modules", []))}</div>
    <h3>校准（预测 vs 实测）</h3>
    {calibration_svg(t.get("calibration", []))}
  </div>""")
    legend = " · ".join(f'<span class="mod" style="background:{c}"></span>{n}' for n, c in STATUS.values())
    return f"""<!doctype html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>学习进度</title>
<style>
  body {{ font-family: "PingFang SC", -apple-system, sans-serif; color: #1b2430;
         background: #f5f7f6; margin: 0; padding: 32px 20px 80px; line-height: 1.7; }}
  .sheet {{ max-width: 720px; margin: 0 auto; }}
  h1 {{ font-family: "Songti SC", serif; font-size: 26px; margin: 0 0 4px; }}
  .sub {{ color: #77828d; font-size: 13.5px; margin: 0 0 24px; }}
  .card {{ background: #fff; border: 1px solid #e2e7e5; border-radius: 8px;
           padding: 18px 22px; margin: 14px 0; }}
  .head {{ display: flex; align-items: baseline; gap: 12px; }}
  h2 {{ font-size: 18px; margin: 0; }} h3 {{ font-size: 13px; color: #77828d; margin: 16px 0 4px; }}
  .pill {{ font-size: 12px; padding: 1px 8px; border-radius: 10px;
           background: #e7f0ee; color: #14665a; }}
  .pill.paused {{ background: #eee; color: #77828d; }}
  .stats {{ font-size: 13.5px; color: #4c5866; margin: 8px 0; }}
  .strip {{ display: flex; gap: 4px; flex-wrap: wrap; margin: 10px 0 2px; }}
  .mod {{ width: 26px; height: 12px; border-radius: 2px; display: inline-block; }}
  .legend, .foot {{ font-size: 12px; color: #77828d; margin: 4px 0 0; }}
  .empty, .empty-state p {{ color: #77828d; font-size: 14px; }}
</style></head><body><div class="sheet">
  <h1>学习进度</h1>
  <p class="sub">生成于 {today} · 今日到期卡片共 <b>{total_due}</b> 张</p>
  {"".join(body)}
  <p class="foot">{legend}</p>
</div></body></html>
"""


def main():
    tracks = load_tracks()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(tracks), encoding="utf-8")
    print(f"dashboard: {OUT} ({len(tracks)} tracks)")


if __name__ == "__main__":
    main()
