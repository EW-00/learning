# learning

我的私人 AI 家教工作区。说一句「我想学 X」即可开学；家教负责选材、排课、上课、出题、判卷、复习调度和进度追踪。设计依据 2024–2026 教育科学实证研究，规则总纲见 [TUTOR.md](TUTOR.md)。

## 结构

```
TUTOR.md                  # 家教宪法（十条护栏 + 五循环）
.claude/skills/tutor/     # 家教 skill 本体（clone 即装）
tracks/<科目>/            # 每科一目录：章程/路线图/状态/卡片/错题/考卷/项目
inbox/REVIEW_QUEUE.md     # 每日生成的迷你复习包（有到期卡时）
dashboard/index.html      # 进度可视化（会话后自动重绘）
reports/                  # 每周学习报告
tools/gen_dashboard.py    # dashboard 生成器
```

## 新机器上手

```bash
git clone git@github.com:EW-00/learning.git ~/learning
cd ~/learning
# 可选：全局触发（不在 repo 目录也能说「我想学 X」）
ln -s ~/learning/.claude/skills/tutor ~/.claude/skills/tutor
```

之后在 Claude Code 里说「我想学 X」或 `/tutor` 即可。

## 隐私红线

本 repo 是 **public** 的：
- ✅ 学习笔记、错题、进度、复习卡片
- ❌ 客户信息、公司内部信息、个人隐私、任何凭证

## 定时任务（仅个人 Mac）

- 每日 09:00 — 检查全部 track 的到期卡片，有则生成 `inbox/REVIEW_QUEUE.md` 并推送通知
- 每周日 20:00 — 生成周报到 `reports/`

由 Claude Code 内置 cron 驱动，其他机器无需配置（开课时会自动补做到期复习）。
