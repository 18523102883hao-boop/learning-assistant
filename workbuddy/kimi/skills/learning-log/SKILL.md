---
name: learning-log
description: 学习证据记录。每次作业辅导、探索任务或伙伴闲聊结束时写入当前孩子的学习事件档案。只记录可观察事实，区分观察与推断；闲聊只记场景计数不记内容；模型解释不等于事实。
---

# 学习证据记录

## 触发

作业辅导、探索任务或伙伴闲聊结束时（homework-help / explore-task / partner-chat 的最后一步调用）。

## 写入规则

- **写哪个档案**：只写当前 `child_id` 的档案文件（如 `profiles/momo/learning-log.jsonl`）。新任务、换设备后仍写回同一档案，不新建。
- **一条事件一个 JSON 行**，字段见 `schemas/learning-event.schema.json`。
- **`scene_type` 必填**：`homework`（作业辅导）/ `explore`（探索创作）/ `partner`（伙伴闲聊）。`partner` 场景**只记一次对话一条计数**（subject 记 `partner_chat`，无其他字段），不记聊天内容摘要——闲聊内容不进学习档案。
- **观察 vs 推断**：`attempt_summary`、`outcome` 只写可观察事实；"待验证的学习习惯假设"单独放 `observation_or_inference` 字段并标注待验证。
- **不记**：人格/动机结论（"懒惰""不认真"）、以一次表现推断整个单元掌握、以聊天时长/短回复推断态度。
- **可更正**：孩子或家长指出记录有误时，追加更正条目，不静默改写历史。

## 最小字段

`child_id`、`session_id`、`event_id`、`timestamp`、`scene_type`、`subject`、`skill_id`（无教材映射时可空）、`attempt_summary`、`hint_level`（0–4）、`outcome`（`needs_more_help` / `with_support` / `independent` / `transfer_delayed`）、`evidence_ref`、`observation_or_inference`（标注类型）。

## 提示层级口径

- 0：无帮助独立完成。
- 1：目标/条件提示。
- 2：具体提示或图示。
- 3：同类例题演示。
- 4：换讲法后完成。

## 掌握状态口径（写档案摘要时用）

`待观察` / `辅助下完成` / `独立完成` / `延迟迁移成功`。只有"换数字或换情境的新题独立做对"才更新为延迟迁移成功；当天原题做对不算。

## 隐私

- 记录中不写生僻个人信息；作业照片优先裁掉姓名、学校。
- 孩子档案与孩子入口不混存另一个孩子的记录；家长报告从学习事件生成，走 `parent-review`。
