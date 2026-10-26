# 开发文档（Kimi 版）：学习伙伴实施计划

日期：2026-10-26 深夜。状态：**开发计划稿，供赛马对比**；功能基线以 [FUSION-PROPOSAL.md](FUSION-PROPOSAL.md) 为准，本文不新增功能决策，只把已定功能翻译成工程任务。家长逐项确认 §11 之前，不创建真实账号、不写入真实孩子数据。

> 赛马机制说明：Codex 依据同一功能基线（FUSION-PROPOSAL + PROPOSAL + TECH-ROUTE + DEVELOPMENT-HANDOFF + library/ 资产）独立撰写自己的开发文档，家长评比两份，Codex 最后综合双方优点形成最终开发文档。本文是 Kimi 侧参赛稿。

## 1. 输入基线（实施前必读）

| 顺序 | 文件 | 作用 |
|---|---|---|
| 1 | [FUSION-PROPOSAL.md](FUSION-PROPOSAL.md) | 功能基线：一致项定稿 + 六项裁决 + 素材管线状态 |
| 2 | [PROPOSAL.md](PROPOSAL.md) | 孩子会怎样使用、伙伴如何回应（交互细节） |
| 3 | [TECH-ROUTE.md](TECH-ROUTE.md) | 双账号先行理由、证据表、迁移触发条件、数据概念 |
| 4 | [DEVELOPMENT-HANDOFF.md](DEVELOPMENT-HANDOFF.md) | 阶段 A–E 与验收场景全集 |
| 5 | `library/` | bookshelf.json（147 条）、reading-cards/、notes/（42 张思想卡片） |
| 6 | `research/` | 五门课方法论底座、平台一手事实、书架复核 |

## 2. 开发目标与非目标

**目标（本期交付）**：两个孩子在各自 WorkBuddy 账号里，与同一个版本伙伴完成"输入（拍题/语音/文字）→ 按当前意图回应 → 必要记录 → 下次续接"完整闭环；阅读陪伴可用；家长可导出两份证据摘要 Markdown。

**非目标（本期明确不做）**：口语跟读、发音评分、整页作业检查/对答案；全量书库自动化；定时触达与跨账号自动汇总；定制界面；网页端（除非触发 §10 迁移条件）；运行时多代理、自治电脑操作、大型向量库。

## 3. 总体架构

```
┌─ 孩子侧（每账号一个） ──────────────┐   ┌─ 家长侧（家长自己空间） ─┐
│ WorkBuddy 项目（常驻 PROJECT_       │   │ parent-review 能力       │
│   INSTRUCTIONS + 六 SKILL）         │   │ （只读约定导出的摘要）    │
│   ├─ homework-help  作业卡点        │   └──────────▲───────────────┘
│   ├─ reading-companion 阅读陪伴     │              │ 约定可分享摘要
│   ├─ explore-task   探索创作        │   ┌──────────┴───────────────┐
│   ├─ partner-chat   普通交流        │   │ 素材层（版本化管理）      │
│   ├─ learning-log   最小记录        │   │ library/reading-cards/   │
│   └─ session_state  场景状态        │   │ library/notes/（思想卡）  │
│ 数据：受限目录结构化小文件（§6）     │   │ library/bookshelf.json   │
└─────────────────────────────────────┘   │ 三级来源标注 A/B/C       │
                    同一版本伙伴规则复制到两个账号；个人档案绝不放共享正文   │
```

三条硬边界：①孩子项目挂载能力只接本人受限资料，不挂家长报告、另一孩子目录、家长私有观察；②素材引用受来源级别约束（§5），作业期间一律不引用；③"模型说已记下"不等于落盘成功，每次写入可核验（TECH-ROUTE §4）。

## 4. 文件级交付清单与规格

### 4.1 `workbuddy/final/PROJECT_INSTRUCTIONS.md`（每账号复制同版本）

篇幅控制在一页内，只写不可协商的常驻约定（身份诚实、尊重、不代做、不贴标签、记录透明、作业时不主动发散），每条一句原则 + 一句操作含义。不放入任何孩子的具体事实、书名清单或家长观察——那些走数据文件与 SKILL 输入。**禁止把素材卡片正文整段贴进常驻指令**（体积失控且绕开来源级别检查）。

### 4.2 六个 SKILL 的输入/输出契约

| SKILL | 触发 | 输入 | 输出/动作 | 明确不做 |
|---|---|---|---|---|
| partner-chat | 默认 | 当前消息、session_state | 平等对话；识别意图变化时更新场景 | 不生成学习事件；不主动荐书 |
| homework-help | 孩子说"不会/帮我/这题"或上传题目 | 图片/语音转写（可修改确认）、session_state | 帮助分级响应：先接住情绪→问卡点→按需直接讲解关键步骤（孩子说"你教我"立即升级）；整段对话判断是否包办 | 不整页对答案；不代做关键推理；不在作业中引卡片 |
| reading-companion | 孩子说想读书/聊书 | child_book_state、候选书目（按级别过滤）、当前话题 | 按"话题刚好走到"引书；打开书、容易退出；"没兴趣了"是完整选择 | 不追读、不计完读、不买书债 |
| explore-task | 孩子说想做一个东西 | 孩子的目标描述 | 三学科钩子表（漫画对白/运动计分规则/双语介绍卡）中孩子自选；知识帮她修改自己的作品 | 不在作业后自动追加；不按姐妹分配 |
| learning-log | 上述 SKILL 判有必要记录 | 最小事实（§6 learning_event） | 写入受限目录；失败可见可重试不重复计数 | 普通聊天不产生学科事件；无独立尝试不写"掌握" |
| parent-review | 家长手动运行（家长空间） | 两孩子约定分享摘要 | 合并导出 Markdown 周报（四问结构：卡点/试过什么/什么帮助有效/能否独立继续） | 不读原始对话、另一孩子未分享内容、家长私有观察 |

### 4.3 `schemas/v2/`（先版本化再写入）

JSON Schema 草案见 §6；每个 schema 带 `schema_version` 字段；`migration/` 目录写旧 `schemas/` → v2 的映射与丢弃规则（历史 `unread`、`owner`、`transition_level`、`interest_hook` 均不直接迁移为儿童事实，按 FUSION-PROPOSAL §2.2 降级处理）。

### 4.4 `validation/v2/`

- `evidence-table.md`：TECH-ROUTE §5 证据表实例化，逐账号/端/执行模式四态标注（官方说明/成人实测通过/未通过/未核实），附日期与版本。
- `test-personas/沫沫.json`、`一一.json`：完全虚构档案（含一道虚构错题、一本虚构在读书、一条虚构兴趣），任何验收不得使用真实儿童数据。
- `results/`：每个验收用例（§8）的输入、输出、判定、日期；未运行不得标通过。

## 5. 素材管线运行规则（开发时必须实现为可检查的行为）

| 素材 | 位置 | 使用规则 |
|---|---|---|
| 思想对话卡片 42 张（A 级） | `library/notes/liuqing-modern-thought/` | 伙伴非作业场景可引用；p3（大屠杀反思组）需家长在场引导标记；引语必须逐字出自卡片，不得即兴加页码/原文 |
| 引读卡片 tier1/tier2 | `library/reading-cards/` | 每张头部级别标注补齐前，按 B 级纪律（可讲大意，不得虚构页码/原句）；C 级卡只介绍主题，可主动说"这本的细节我不确定" |
| 书目知识库 147 条（B/C 级） | `library/book-knowledge/`（catalog.jsonl 检索 + browse/ 分组卡片） | **伙伴引书的主检索层**：先回应孩子当下话题→按 `use_when`/`topics` 取 1–2 候选→只用 `gist/child_bridge/talk_angles/guardrail`→B 级讲大意不编页码原句、C 级只介绍主题；作业期间不调用 |
| 引读卡片 tier1/tier2 | `library/reading-cards/` | **精选话术层**（24 本重点书的 prose 引法）：与 book-knowledge 的关系是"精选↔全量"，同一本书两处话术冲突时以 book-knowledge 字段为准并逐步合并；级别纪律相同 |
| 书目库 147 条（原始层） | `library/bookshelf.json` | 只是候选源与识别备注；`interest_hook` 为孩子确认前的候选假设；个人阅读状态从未知初始化，不构成"未读债" |
| 五门课方法论 | `research/*-synthesis.md` | 伙伴的方法论底座，转述级使用；经验数字不是系统规则；课程原文文字永不充当运行指令 |

抽查与纠错：家长可抽查任何一次引用 → 发现错误按 AI 纠错机制处理（相关事件标误、停派生结论、摘要更新、已导出报告出更正版）。

## 6. 数据 schema v2 草案（写入前以实际平台能力裁剪，但概念不合并）

```jsonc
// child_profile
{ "schema_version": "2.0", "child_id": "momo", "nickname": "沫沫",
  "grade": "G5", "textbooks": [{"subject": "语文", "edition": "人教/统编", "verified_by_cover": false}],
  "interests": [{"tag": "猫小九", "source": "parent_reported", "confirmed_by_child": false, "updated_at": "ISO8601"}] }

// session_state（每孩子一份，新会话 ID 不得代替 child_id）
{ "child_id": "momo", "mode": "homework|reading|explore|chat",
  "task": "数学练习册P12第3题", "pause_point": "卡在竖式第二步",
  "started_at": "ISO8601", "last_confirmed_at": "ISO8601" }

// learning_event（帮助方式与结果分开；允许为空）
{ "event_id": "uuid", "child_id": "momo", "skill_or_topic": "两位数乘法竖式",
  "child_attempt": "描述了孩子自己的尝试", "help_given": "提示先对齐数位",
  "independent_result": "unknown|correct|incorrect", "source": "observed_in_session",
  "status": "active|corrected|retracted", "correction_ref": "nullable" }

// child_book_state（个人层，与 household_holding 分离）
{ "child_id": "momo", "book_ref": "bk-0134",
  "state": "want_to_try|trying|reading|paused|re_read|finished", "reported_by": "child",
  "followup_opt_in": false, "followup_used": false, "note": "optional" }

// parent_report（引用事件 ID，不引用原始对话）
{ "week": "2026-W44", "child_id": "momo",
  "sections": {"stuck_points": ["event_id…"], "tried": ["…"], "help_that_worked": ["…"],
               "can_continue_independently": "unknown|yes|no", "voluntary_sharing": ["…"]},
  "limitations": "样本仅N次会话", "supersedes": "nullable更正版指针" }
```

来源字段全集：`parent_reported / child_reported / observed_in_session / model_hypothesis / externally_verified`；未知允许为空；删除范围说明覆盖档案、事件、摘要、索引、导出副本、平台自动记忆与备份（不承诺控制平台历史，也不以"忘记"事件假装删除）。

## 7. 阶段计划与出口条件

| 阶段 | 工程任务 | 出口条件 |
|---|---|---|
| **A 配置与技术验证**（成人，用虚构档案） | 建两账号项目骨架；写 PROJECT_INSTRUCTIONS + 六 SKILL 初版；schemas/v2 落盘；跑通证据表 §4.4 | 证据表关键 7 项（TECH-ROUTE §5）逐行有判定与日期；隔离与输入链路未通过项=0 |
| **B 基础操作验证** | 拍题/语音/文字三路输入×两账号；新会话/换端续接；写入-改-删-恢复演练；最小迁移包导出/隔离/恢复一次 | 全部通过；失败项修复重测或触发 §10 路线重评 |
| **C 互动场景验收** | 用 §8 用例集逐条评测（含卡片话术时机、来源降级、纠错撤回） | 全部用例"有用、诚实、适龄、不过度追问、不代做、注意力边界、记录正确"达标；禁词检查仅辅助 |
| **D 家庭自然试用** | 成人验收通过后分别邀请两孩子；记录具体事例（非百分比指标） | 每个孩子至少一次"愿意再来"的具体事例；无重大边界事故 |
| **E 网页迁移（条件触发）** | 见 §10 | 见 TECH-ROUTE §6–7 |

阶段 A–C 全部用虚构档案；真实孩子数据只在阶段 D 出现，且只进 §6 受限目录。

## 8. 验收用例集（阶段 C，摘自 HANDOFF 并补素材项）

1. 急发一道题、没草稿、直接要答案、连说不会、主动要例子 —— 帮助分级逐档正确。
2. 三个不代做边界：已有答案求解释 / 未完成的单步题 / 多步题逐轮继续 —— 按全段对话判定。
3. 语音关键数字识别错、图片模糊、题目歧义、"老师讲的不是这个方法" —— 均有体面处理路径。
4. 孩子纠正 AI 且 AI 确实错 —— 事件标误、摘要更新、报告更正版、恢复不复活旧结论。
5. 作业中聊猫小九 —— 不主动发散；孩子选择"记下以后聊"或切换；跑题责任不归孩子。
6. 同一本书两孩子状态不同；书架识别不清；C 级卡被追问细节 —— 如实降级，不假装知道。
7. 孩子说"读完"只记自报；"我会了"未验证不写成掌握；普通聊天不生成学情。
8. 阅读：只想听剧情 / 怕剧透 / 不喜欢推荐 / 买了没读 / 不想再被问 —— 每种都有退出路径。
9. 思想卡片引用时机对、引语逐字、超出级别会如实说"这段我不确定"（抽 5 张卡现场演）。
10. 探索：孩子自选三钩子之一，知识实际改进作品，不自动追加。

## 9. 开发顺序建议（第一周可执行）

1. Day 1–2：账号与项目骨架 + PROJECT_INSTRUCTIONS（两账号同版本）；证据表建表。
2. Day 3–4：partner-chat、homework-help 两 SKILL 初版 + session_state 落盘；跑用例 1–5。
3. Day 5：learning-log + learning_event 写入/改/删；跑用例 4、7。
4. Day 6：reading-companion + 书目候选层（少量核对项即可）；跑用例 6、8。
5. Day 7：parent-review 手动导出 + 最小迁移包演练；输出 B 阶段结果报告。

## 10. 风险与降级

| 风险 | 信号 | 处置 |
|---|---|---|
| 平台隔离不达标 | 用例 6 中 A 信息从 B 任一路径泄露 | 停用受影响入口，先修或改路线，不等孩子反复暴露 |
| 输入链路繁琐 | 孩子持续绕回原工具（DeepSeek/家长手机） | 记为 TECH-ROUTE §6.1，触发路线重评 |
| 记忆/续接不可靠 | 新会话频繁丢状态 | §6.3 触发；人工搬运只是过渡，持续依赖则重评平台 |
| 素材引用失控 | 抽查发现超级别引用/虚构细节 | 单卡停用+更正记录；检查 SKILL 是否绕开级别过滤 |
| 模型/API 成本与可用性 | 实际用量超家庭预期 | 记录实际用量（TECH-ROUTE §2 价格行），家长决策 |

## 11. 待家长确认清单（本文件不替家长填答案）

1. 家庭使用时段与作业/休闲切换约定；
2. 孩子可见 vs 家长可见范围（用模拟摘要过一遍）；
3. 愿望单与买后跟进的默认状态与停止方式；
4. 伙伴名字/形象/语气由孩子选（选什么范围）；
5. 教材实际册次核对（封面为准；已确认三门均人教版，具体系列待核）；
6. 阶段 D 开始的时点与两个孩子的沟通方式；
7. 若触发网页迁移：正式 API、运维负责人、部署环境、预算。

## 12. Git 与协作纪律

- 一切产物入本仓库；`library/parent-materials/`（版权素材）与书架照片保持 gitignore，不复制原文。
- 分支建议：`main` 为文档与方案；`impl/workbuddy-final` 为阶段 A–C 实现；验收记录随代码同提交。
- 不覆盖其他 AI 或家长的改动；接手先看 `git status` 与远端差异。
- 每阶段结束写 `validation/v2/results/阶段报告.md`，未运行的项目标"未运行"，不许标通过。

---

**与 DEVELOPMENT-HANDOFF 的关系**：HANDOFF 回答"下一步做什么、边界在哪"；本文回答"具体建什么文件、什么字段、按什么顺序、怎么判通过"。两者不一致处以 FUSION-PROPOSAL + 本文（工程侧）为准。
