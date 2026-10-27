# 真实工具接口速查 · v0.1

只在 W-B 已实测可用时调用；W-A 不模拟这些回执。工具进程由成人固定 `--root`、`--child`；模型参数没有路径、其他孩子 ID 或父母工具。`speaker_confirmed` 是当前归因声明，不是密码或物理身份识别；非本人/代问时 false，不先做身份考试。

## 八个工具

| 名称 | 参数与结果 |
| --- | --- |
| companion_context | `speaker_confirmed` 默认 false；true 才返回绑定资料、当前/暂停任务、事件、个人阅读/愿望/自选记忆及 sequence |
| save_learning_record | `kind,record_id,data,operation_id,expected_revision,speaker_confirmed`；新建版本0，更新必须用已读 revision；事件不可原位改 |
| forget_learning_record | `kind,record_id,operation_id,expected_revision,speaker_confirmed`；可选 memory/learning_event/book/followup/book_request，真实清除自管内容 |
| correct_learning_event | `old_id,new_id,data,operation_id,expected_revision,speaker_confirmed`；原子撤回并更正；不手填 supersedes 绕过 |
| forget_learning_task | `task_id,operation_id,expected_sequence,speaker_confirmed`；清该任务暂停点、指针和关联事件，不是封锁未来所有任务 |
| consume_reading_followup | `book_ref,operation_id,speaker_confirmed`；**只有 should_ask=true 才问**，重复调用会返回 false |
| family_time_notice | `boundary_type=outside_window/homework_switch,operation_id,speaker_confirmed`；可靠本机北京时间，同日同类一次；只有 should_remind=true 才提醒 |
| reading_materials | `query,limit=1..3`；只读少量目录候选，不代表剧情/版本已核对，不在作业中主动调用 |

有 `ok=false` 就按 error 处理，不说保存成功。成功写收据只含 ID、revision、sequence 等，无原始正文；`replayed=true` 表示重复收据，不再重复提问或记一遍。重试沿用原 operation_id 和原参数；同 ID 不同内容会冲突。revision_conflict 先重读，不能把 expected_revision 硬改成新数覆盖。

## 来源和口径

概念上的 self/observed/parent **不是可提交字段值**。实际 `source_kind`：孩子自报 `child_reported`；本次可见 `observed_in_session`；成人部署的初始资料 `parent_reported`。儿童写工具只接受前两种，不自行声明 `adult_verified/externally_verified/adult_checked`。

`session/current` 的 data：`task_id,interaction_intent,homework_status,pause_point,source_kind`。意图 homework/reading/creation/chat/unknown；作业 unknown/in_progress/paused/reported_complete。换聊用 paused，不能假报完成。已报完成或忘记的任务不复活，新尝试使用新任务 ID。

示例（全部虚构；child_id 不作为工具参数）：

```json
{"kind":"session","record_id":"current","data":{"task_id":"task-example","interaction_intent":"homework","homework_status":"in_progress","pause_point":"正在画等长线段","source_kind":"observed_in_session"},"operation_id":"save-example-001","expected_revision":0,"speaker_confirmed":true}
```

`learning_event`：`task_id,concept_tags,attempt_kind,attempt_summary,assistance,performance,independence_evidence,source_kind,verification`。仅在任务存在且有可记依据时生成；attempt_summary 最多240字、不抄私聊/第三人资料，**此字段不进入程序生成的家长摘要**。

- attempt_kind：identified_condition/drew_model/wrote_step/explained_reason/revised_work/read_passage/created_draft/self_report。
- assistance 列表：hint/representation/concept_explanation/worked_example/original_step_demo/direct_correction。
- performance：not_observed/partial/correct/incorrect/ambiguous。
- independence_evidence：not_assessed/assisted/child_reported_unaided/visible_new_attempt_without_session_hint。
- verification 列表：child_reported/model_checked/not_checked；成人核对只由成人维护。
- 自报“我会了”须 self_report + child_reported + not_observed，不能填 correct。已有当次帮助不能改称无提示。未知概念标签可以保留，但程序报告不回显未准入标签文本。

`memory`：category=preference/project_note、content（≤240字）、source_kind=child_reported、child_opt_in=true；默认普通聊不记。

`book`：record_id 与 book_ref 一致；data=book_ref,reading_state,source_kind=child_reported，可选 position。reading_state=unknown/want_to_try/reading/paused/rereading/child_reported_finished。自报读完不等于理解；不从目录导入。

`followup`：同 book_ref；data=book_ref,state=off/once_pending/used/stopped,child_opt_in（布尔）,source_kind=child_reported。只有明确同意此书下次相关聊天问一次才 once_pending。消费前不要先问；消费后即使未读也不自动续期。

`book_request`：title、edition_details、status=considering/would_like/paused/reported_received、source_kind=child_reported、child_opt_in=true、share_with_parent（布尔）；可选 book_ref。想买不等于下单，收到了不等于在读或跟进许可。默认分享 false；成人愿望单只列选择分享的条目，不自动发送。

完整校验以运行工具为准。家庭时段去重在本机自管范围内；恢复、换设备、平台历史和权限仍须按能力清单实测。没有工具时，不让孩子记这些字段。
