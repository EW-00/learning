# 循环 D · 复习引擎：FSRS-lite

复习就在家教会话里做，不引入 Anki——LLM 能追问、能诊断，比翻卡深一层。调度用 FSRS 的语义，不用 21 参数公式。

## 卡片 schema（`tracks/<slug>/cards.jsonl`，每行一张）

```json
{"id": "mip-007", "type": "concept-contrast", "front": "最大化问题中，LP 松弛的最优值是原 MIP 的上界还是下界？为什么？", "back": "上界。放松约束只会让可行域变大，最优值只会变好或不变。", "source": "Wolsey ch.2 / session 2026-07-06", "stability_days": 4, "difficulty": 6, "last_review": "2026-07-08", "lapses": 1}
```

- `type`：`concept-contrast`（概念辨析，优先）| `derivation-step`（推导关键步）| `transfer-scenario`（何时用 X 而非 Y）| `cloze` | `qa`
- 值得做卡：核心概念辨析、推导关键步骤、条件判断、地基事实。**不值得**：能随手查到的细节、没理解就背的内容、超过一口气能答完的长答案（一卡一事实）
- 新卡初始：`stability_days: 1, difficulty: 5, lapses: 0`

## 调度规则

- **到期判定**：`今天 - last_review ≥ stability_days`
- **出题顺序**：按逾期比 `(今天 - last_review) / stability_days` 降序
- **更新**（复习后立即写回）：
  - 答对且轻松 → `stability ×2.2`（取整）
  - 答对但费力 → `stability ×1.5`
  - 答错 → `stability = max(1, ×0.3)`，`difficulty +1`，`lapses +1`
- **目标保持率 0.85**：session 内错误率维持 20–40% 为健康。全对 → 间隔太保守，下轮乘数上调；错过半 → 该主题退回教学模式，不是继续刷卡
- **翻修**：`lapses ≥ 4` 的卡自动拆分或改写成更小的卡（违反最小信息原则的信号），旧卡删除

## 复习的执行方式（这是 LLM 相对 Anki 的独有优势）

1. **每次改写题面**：同一张卡每轮换表述、换情景、换数值考——`front` 是语义锚点，不是逐字念稿。杜绝「背题面」。
2. **必须是检索**：先出题 → 等她作答 → 反馈紧随其后（有反馈的检索效应翻倍，Rowland 2014）。
3. **交错**：每次混 2–3 个主题的到期卡；易混概念对（如「对偶间隙 vs 整数间隙」）刻意相邻出。纯定义卡不强行交错。
4. **答错的卡**：不只给正确答案——先让她自己找错（「你的答案和 X 矛盾，矛盾在哪？」），找不到再讲。
5. ERRORS.md 里到复验日期的错题，混入本次复习（用平行题考，不用原题）。

## 每日催力（定时任务的行为规程）

每天上午定时任务醒来执行：

1. `cd ~/learning && git pull`
2. 扫描全部 `tracks/*/cards.jsonl` 和 `tracks/*/ERRORS.md`，收集到期项
3. **无到期项 → 静默退出**，什么都不生成
4. 有到期项 → 生成 `inbox/REVIEW_QUEUE.md`：挑最逾期的 5–8 张（跨 track 交错），**题面已改写**，只有问题没有答案；文末注明「回复我或开一次会话来完成」
5. 推送一条通知：「今日复习包：N 张卡，约 5 分钟（涉及 <tracks>）」——只报数量，不制造愧疚
6. commit + push

她完成复习包时（任何会话里）：按上方规则判分、写回 stability、删除 REVIEW_QUEUE.md、commit。她没做 → 下次开课的热身检索自然覆盖，不催第二次、不积压多份 QUEUE。
