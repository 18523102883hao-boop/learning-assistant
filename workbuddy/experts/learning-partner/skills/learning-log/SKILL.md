---
name: learning-log
description: 学习证据记录。作业辅导、探索任务或共读/闲聊结束时，往当前孩子的档案追加一条学习事件（jsonl）。只记可观察事实，分清"她说的/我看到的/我猜的"；闲聊只记场景计数不记内容；写不进去必须明说，不能谎称已保存。字段定义见 references/learning-event.schema.json。
---

# 学习证据记录

## 什么时候写

- `homework-help`、`explore-task`、`reading-companion` 结束时：写一条。
- `partner-chat` 结束时：只写一条场景计数。
- 本次只是随口一问、没有可观察的过程：**可以不写**，不要为了凑记录编内容。

## 写到哪

`child_id` 只认一个来源：`profiles/current.json` 里的字段。**问出来的、猜出来的、她自报的，一律不写。**

按顺序找路径，命中即停：

1. `profiles/learning-log-{child_id}.jsonl`（推荐结构，一个孩子一个文件）
2. 若 `profiles/{child_id}/` 目录存在：`profiles/{child_id}/learning-log.jsonl`
3. 都找不到：在当前工作目录建 `profiles/learning-log-{child_id}.jsonl` 并追加

没有 `current.json`、或 `child_id` 不明 → **本次不写**，也不要建一个"unknown"档案。

## 一条一行，字段如下

完整定义在 `references/learning-event.schema.json`。最小可用形态：

```json
{"schema_version":"1.0","child_id":"momo","session_id":"2026-10-27-1","event_id":"evt-20261027-001","timestamp":"2026-10-27T19:42:00+08:00","scene_type":"homework","subject":"数学","skill_id":"division.grouping","attempt_summary":"能独立圈组，卡在把组数换算成总价","assistance":"具体提示（关系图）","performance":"partial","independence_evidence":"assisted","hint_level":2,"outcome":"with_support","source":"observed_in_session","evidence_ref":null,"observation_or_inference":{"kind":"hypothesis_to_verify","text":"题意转数量关系的环节可能不稳定，需再观察"}}
```

字段要点：

| 字段 | 规则 |
| --- | --- |
| `scene_type` | `homework` / `explore` / `partner` 必填 |
| `subject` | 语文/数学/英语/跨学科；`partner` 闲聊记 `partner_chat` |
| `attempt_summary` | **只写可观察的**：她做了什么、停在哪一步。不写动机、不写人格词 |
| `hint_level` | 0 独立 / 1 目标或条件提示 / 2 具体提示或图示 / 3 同类例题演示 / 4 换讲法后完成 |
| `outcome` | `needs_more_help` / `with_support` / `independent` / `transfer_delayed` |
| `source` | `child_reported` / `observed_in_session` / `parent_reported` / `model_hypothesis` |
| `observation_or_inference` | 一切非事实内容放这里，`kind` 标 `observation` 或 `hypothesis_to_verify` |
| `correction_of` | 更正旧事件时填被更正的 `event_id`；**追加，不改写历史** |

## 口径（写错就污染所有下游报告）

- **`transfer_delayed` 只有一个条件**：换数字或换情境的新题、且这次没给解法提示、独立做对。当天原题做对不算。
- 她说"我会了""我读完了"→ 记 `child_reported`，**不记"已掌握""已理解"**。
- 同一道题反复追问是**一个**任务上下文，不能拆成多次"独立失败"。
- 没看到她的尝试 → `performance: not_observed`，不要留空也不要瞎填。
- 不记：人格/动机结论、以一次表现推断整单元掌握、以聊天时长或短回复推断态度、同学姓名、姓名学校。
- 教材版本未核对 → `curriculum_ref: null`，`skill_id` 只写这道题支持的概念。

## 写不进去怎么办

- 帮助继续，不要中断当前对话。
- **明确告诉她"这次我记不下来"**，不要说"我记住了"。
- 在回复里给家长留一句可操作的话（例如"这次记录没写成功，可能需要检查目录权限"），但不说技术细节给孩子。

## 隐私

- 照片/附件不另存副本；记录里不写姓名、学校、班级。
- 一个孩子的档案里绝不出现另一个孩子的记录。
