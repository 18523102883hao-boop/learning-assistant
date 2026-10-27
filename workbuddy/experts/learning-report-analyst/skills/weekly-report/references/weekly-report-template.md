# 家长周报模板 · 结构化最小导出

用于家长入口。下面的所有标识、日期及例子均为虚构；不能当成任何孩子的真实表现。使用前由家长确认导出对象、期间、来源及最新撤回状态。无法确认时只说明待核缺口，不引用具体事件生成个体结论，不伪称最新。

## 输出模板

```markdown
# 学习互动摘要 · {孩子代号}
期间：{开始} 至 {结束}（北京时间）

**样本与范围**：仅 {实际事件数} 条有效事件；主动求助及未记录部分存在样本偏差，不代表全部作业或学科水平。

## 卡在哪
{具体已准入概念和证据 event_id；无证据写“尚不能确定”。}

## 试过什么
{有效事件中观察到的尝试；自报明确标为自报，不能杜撰过程。}

## 哪种帮助后出现什么
{根据 assistance、performance 和 verification 写关联；不是因果证明。}

## 能否独立继续
{分清 assisted、自报与本会话未见提示的尝试；证据不足写未知，不外推掌握。}

## 家长可以做的一件小事
{有依据时给一个可拒绝、低负担的支持；不新增打卡、练习或比较。}

## 工具错误与更正
{有明确证据才说明；否则写“本次导出无可用记录”。如为更正版，标记 supersedes 并提醒替换旧副本。}

来源：{source_store_id} / {source_sequence}。摘要只反映当前有效导出，不能说明孩子的动机、性格或整体能力。
```

## 最小导出字段示意（虚构）

```json
{
  "schema_version": 3,
  "rule_version": "v3.2026-10-27",
  "child_id": "test-a",
  "source_store_id": "store-test",
  "source_sequence": 3,
  "period": {"start": "2026-10-20", "end": "2026-10-26", "timezone": "Asia/Shanghai"},
  "events": [{
    "event_id": "event-1", "task_id": "task-1", "observed_at": "2026-10-25T11:00:00+00:00",
    "write_sequence": 3, "concept_labels": ["应用题数量关系"],
    "attempt_kind": "identified_condition", "assistance": ["representation"],
    "performance": "partial", "independence_evidence": "assisted",
    "source_kind": "observed_in_session", "verification": ["not_checked"]
  }]
}
```

这仅示范数据形状，并不证明真实数据来源、最新性、被撤回情况或专家与工具已经连接。
