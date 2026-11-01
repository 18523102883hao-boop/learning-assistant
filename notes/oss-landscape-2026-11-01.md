# 开源项目选型：能给「沫沫与一一的学习伙伴」补什么

日期：2026-11-01。数据来源：GitHub REST API 实测（`repos/{owner}/{repo}`、`search/repositories`），star／许可证／最后提交均为当日实测值。
对应文档：[完整方案](final-plan-2026-10-27.md)、[工程规格](engineering-plan-2026-10-27.md)。

## 0. 三句话结论

1. **你的方案不缺设计，缺三样工程件**：身份与记忆隔离、可机器判定的学习证据、客观掌握度算法。这三样都有成熟开源件。
2. **但 GitHub 上没有现成的「家长可查证据链」和「多孩子档案隔离」** —— 全部教育类项目都是单学生模型（single `User`）。这两件正好是你方案的核心，也就是说**你不是在重复造轮子，你是在填空白**。
3. **在决定「自建网页」之前，先花半天评估 `HKUDS/DeepTutor`** —— 你 §16.4 设想的网页形态，它已经做完了大部分基础设施。

## 1. 最值得先看的一个：HKUDS/DeepTutor

| 项 | 值 |
| --- | --- |
| 仓库 | `HKUDS/DeepTutor` |
| star | 52,825 |
| fork | 6,466 |
| 语言 | Python（Next.js 16 前端） |
| 许可证 | Apache-2.0 |
| 最后提交 | 2026-10-31 |
| 出品 | 香港大学数据智能实验室（HKUDS） |
| 论文 | arXiv 2604.26962 |

与本案的重合点：

| 本方案的硬需求 | DeepTutor 已有能力 | 对应章节 |
| --- | --- | --- |
| 孩子/家长两种角色、家长单独空间 | v1.6.3 起 **learner / guardian accounts** | §3、§5.4 |
| 两个孩子档案互不可见 | v1.4.3 起 real per-user isolation；Workspaces 分离主题文件与学习状态 | §5.2、G05 |
| 家长看到「有据可查」的证据 | **Inspectable memory：L1 traces / L2 facts / L3 synthesis + Memory Graph 可审计证据链** | §12.1、§12.4 |
| 更正、忘记、撤回 | 记忆可编辑；归档会话可永久删除；回收站 | §5.4、T32、T35 |
| 一本共有书、两人状态不同 | v1.6.0 **shared Books with private learning state** | T23 |
| 记忆有边界、不膨胀 | v1.6.15 **bounded tutoring memory** | G04、§5.5 |
| 掌握度路径 | **Mastery Path**：目标拆成知识点地图，每点带 mastery gate（不达标不放行）+ mastery evidence | §7.7 |
| 纸题拍照进电脑 | MinerU 解析接受 PDF／图片／DOCX／PPTX／XLSX；图片可送视觉模型 | §6.1 |
| 语音输入 | Voice 分组含转写与合成（小米 MiMo、MiniMax 等） | §6.1 |
| 家里的书进入伙伴 | Books／Reading／EPUB 标注／知识库（LlamaIndex、PageIndex、GraphRAG、LightRAG） | §9.1、§16.3 |
| 中文 | v0.6.0 起完整中文本地化；有微信／飞书社群 | — |
| 部署门槛 | `docker run` 一条命令；`pip install "deeptutor[full]"`（Python 3.11–3.14 + Node 20.9+）；或 **桌面安装包**（自带 Python 与 Node，免终端） | §15.4 |

**实话（不能只看 README）：**

- 大系统，功能面远超本项目需要，上手与长期维护成本要按实际估。
- 教学法是通用型，不含「小学生不代做作业」这一层。你 §7 的**可跳级帮助方式**、§12 的**证据口径**仍是你独有、必须自己做的部分。
- 迭代极快（几乎每周发版）→ **钉住一个 release tag，不要跟 main**，并记录版本号。
- Apache-2.0 允许商用改造，二次分发需保留声明。

## 2. 中文课标对齐：cn-math-taxonomy

| 项 | 值 |
| --- | --- |
| 仓库 | `xiaoyang111222/cn-math-taxonomy` |
| star | 5,655（fork 1,450） |
| 许可证 | **CC BY-NC 4.0（署名—非商业）** |
| 最后提交 | 2026-10-31 |

实测数据：

| 文件 | 大小 | 内容 |
| --- | --- | --- |
| `data/topics.json` | 2.6 MB | 2,997 个知识点（语文 493／数学 870／英语 791／物理 269） |
| `data/dependencies.json` | 880 KB | 2,403 条先修边，分 **hard / soft** |
| `data/cn-curriculum-standards.json` | 324 KB | 2022 课标条目映射 |
| `data/questions.json` | 7.8 MB | **12,135 题**，带 answer / explanation / verify |

小学段知识点分布（按你两个孩子的年级）：小一 189 个／**小三 268 个**／**小五 281 个** —— 一一和沫沫的年级段都有覆盖，可先跑这一步验证够不够用。

题目单条结构（实测样例）：

```json
{"difficulty":"basic","type":"numeric","prompt":"3 的后面一个数是几？",
 "answer":"4","explanation":"从 1 往后数，3 的后面是 4。",
 "verify":"3+1","id":"cnm_p001_q1","topicId":"cnm_p001"}
```

四个字段对本案是实质升级：

1. **`topicId`** → 直接作为 `learning_event` 的「具体概念标签」，不用模型自由生成。
2. **`explanation`** → 分层提示的取材来源。§7.2 的可跳级帮助需要「有真实表示／示范」，这是现成素材且来源可标。
3. **`verify`** → **可执行验证式**。这一条最重要：§5.1 写「模型判断不是事实来源本身」，有了它，对错可机器判定。`performance` 字段（correct／incorrect）因此有客观依据。
4. **`mastery_criteria` / `diagnostic_question`** → 每个知识点自带 2–3 条掌握标准与诊断题，可直接填 `independence_evidence`。

**用法上最关键的一条**（`diagnose/` 的实现）：答错时**沿先修边回溯**，而不是原地重复讲。五年级分数应用题错了，诊断器会顺着 hard/soft 边一路退到三年级「分数的初步认识」这样具体的点。这直接解决「孩子数学掉队」的真实成因——多数不是当堂没听懂，是上游某点塌了。

**许可证限制：** CC BY-NC 4.0 是**非商业**授权。自家孩子用没问题；若日后产品化（§15 的长期路线），这层要重估或自建题库。自述为 AI 生成初稿，**题目需抽样复核**。

## 3. 教学法引擎：把「不代做」变成结构保证

| 仓库 | star | 语言 | 许可证 | 最后更新 | 可复用点 |
| --- | --- | --- | --- | --- | --- |
| `CAHLR/OATutor` | 274 | JS | MIT | 2026-10-31 | **最值得抄的教学引擎** |
| `zijinz456/OpenTutor` | 159 | Python | MIT | 2026-10-31 | `learning_science/` 独立封装 BKT、难度选择、认知负荷；FSRS 4.5 + 学习者记忆图；Socratic mode 答案强制引用原文 |
| `Li-Evan/Bloom` | 295 | JS | MIT | 2026-10-20 | Bloom 2-Sigma：`syllabus→lesson→annotate→feedback→evaluation` 状态机，天然产生可回溯证据链；有 CLI 与 Web 两形态 |
| `plastic-labs/tutor-gpt` | 933 | TS | GPL-3.0 | 2026-02-20 | Theory-of-Mind 学生建模；每轮后由模型**重写下一轮教学 prompt** |
| `ECNU-ICALK/EduChat` | 975 | Jupyter | 无许可证 | 2025-07-18 | 华东师大中英教育对话大模型（7B，需 GPU），仅作语料／SFT 参考 |

**OATutor 的具体实现细节（这是真正能落地的部分）：**

| 文件／开关 | 作用 |
| --- | --- |
| `HintSystem.js` + `HintTextbox.js` | hint 纯文本／scaffold 需作答，两种提示形态 |
| hint pathway JSON | 每道题按 step 挂提示路径：第 1 层问「你卡在哪一步」→ 第 2 层给公式 → 第 3 层给半成品算式 |
| `giveStuBottomHint = false` | **关掉最后一条含答案的 bottom-out hint**，等于「永不直接给答案」 |
| `giveHintOnIncorrect` | 答错**强制进提示路径**，而不是重问一遍 |
| `enableCompletionMode` | 掌握达标才允许结课 |
| `BKT-brain.js` + `bktParams.json` | `probMastery / probTransit / probSlip / probGuess` 四参数标准 BKT 更新 |
| `skillModel.json` | 知识点之间的先修关系 |

**这是全文最重要的一条工程启发：**
把「不直接给答案」从**提示词祈求**改为**数据结构保证** —— 答错时状态机自动进入提示路径，而不是每轮靠模型自觉。这直接加固 §7.2 与 T02／T05／T06。

第二条：BKT 让「掌握」从模型自评变成**可计算量**（家长端可展示「分数通分掌握度 0.42→0.81，可点开看是哪几道题推动的」），正好补上 §5.1「模型判断不是事实来源本身」这句的自相矛盾。

## 4. 学习证据链（家长周报的底层）

| 仓库 | star | 语言 | 许可证 | 最后更新 | 用法 |
| --- | --- | --- | --- | --- | --- |
| `adlnet/ADL_LRS` | 334 | Python | Apache-2.0 | 2025-11-14 | ADL 官方 xAPI LRS，对齐 IEEE 9274.1.1。**证据链存储层**：每次练习／对话产出 statement，家长端只读 statement，不由模型复述 |
| `learning-commons-org/evaluators` | 87 | TS | 代码 MIT／内容 CC BY 4.0 | 2026-10-31 | **用学习科学 rubric 给 AI 讲解打分**，发 npm／PyPI 包。家族含 Grade Level Appropriateness（适龄）、Academic Standards Alignment（课标对齐）、Feedback（反馈质量）、Text Complexity。把分数连同原文一起存进学习记录，家长看到的是可复核的评分而非模型自夸 |
| `learningequality/kolibri` | 1,163 | Python | MIT | 2026-11-01 | 抄它的 **coach 视图数据模型**（每 learner × 每 exercise 掌握度），不抄技术栈 |
| `oppia/oppia` | 6,951 | Python | Apache-2.0 | 2026-10-31 | 参考 `learner_goals` 这类显式状态表，**避免用 LLM 生成「学习报告」** |
| `openedx/openedx-platform` | 8,213 | Python | AGPL-3.0 | 2026-10-31 | 参考 `track` 事件表结构（谁／何时／哪个知识点／结果）做埋点设计 |
| `instructure/canvas-lms` | 6,893 | Ruby | AGPL-3.0 | 2026-04-30 | 参考 outcome → rubric → mastery 的口径定义 |
| `wttwins/wrong-notebook` | 801 | TS | 无 LICENSE | 2026-08-22 | 错题本 schema 可直接借：ErrorItem + KnowledgeTag 邻接表（带「1.2.1」编码）+ PracticeRecord + 掌握度统计。但只有单 `User`，child_id 需自己加 |

**不建议引入 Canvas / Open edX 本体**：AGPL + 运维成本，两个孩子用不上，只借数据模型。

## 5. 记忆隔离（当前 WorkBuddy 最大的不确定项）

| 仓库 | star | 许可证 | 最后更新 | 用法 |
| --- | --- | --- | --- | --- |
| `mem0ai/mem0` | 68,172 | Apache-2.0 | 2026-10-30 | 源码级 `user_id` / `agent_id` / `run_id` 三元作用域。child_id 当 user_id，agent_id 固定 tutor，检索强制带 filter |
| `topoteretes/cognee` | 32,966 | Apache-2.0 | 2026-10-30 | 显式 multi-tenant + dataset 级隔离，每孩子一个 dataset |
| `getzep/graphiti` | 32,400 | Apache-2.0 | 2026-11-01 | 按 `group_id` 硬分区；README 明说 MCP server 不鉴权，须自己加 |
| `letta-ai/letta` | 25,310 | Apache-2.0 | 2026-10-18 | agent-per-child 天然隔离（memory blocks） |
| `MemTensor/MemOS` | 12,209 | Apache-2.0 | 2026-10-29 | 「memory cube」可做「家庭共享知识 + 孩子私有记忆」两层 |
| `getzep/zep` | 4,984 | Apache-2.0 | 2026-11-01 | user / thread 两级，经典方案 |

## 6. 儿童安全护栏与回归测试

| 仓库 | star | 许可证 | 最后更新 | 用法 |
| --- | --- | --- | --- | --- |
| `promptfoo/promptfoo` | 26,679 | MIT | 2026-10-31 | **把 T01–T42 变成可回归测试集**。改提示词就跑一遍，防止改坏 |
| `data-privacy-stack/presidio` | 11,615 | MIT | 2026-10-31 | 落库前 PII 脱敏：姓名／学校／住址／电话不进记忆库与日志，对应 T30 |
| `NVIDIA/garak` | 9,814 | Apache-2.0 | 2026-10-27 | 上线前扫描越狱／泄露／幻觉，产出可给家长看的安全报告 |
| `guardrails-ai/guardrails` | 7,575 | Apache-2.0 | 2026-10-31 | 输出侧 schema 校验，防模型编造「已完成／已掌握」，对应 §5.3 |
| `NVIDIA-NeMo/Guardrails` | 7,403 | Apache-2.0 | 2026-10-30 | 可编程对话护栏，定义「小学生模式」话题域与兜底答复 |
| `meta-llama/PurpleLlama` | 4,455 | Llama Community（非 OSI） | 2026-10-30 | Llama Guard 做儿童内容分类；Prompt Guard 挡注入，对应 T37 |
| `unitaryai/detoxify` | 1,312 | Apache-2.0 | 2026-10-20 | 轻量毒性打分兜底 |

已排除：`protectai/llm-guard` 3,220★ 已 **archived**（2026-07-08）。

## 7. 数学与阅读教学能力评测

| 仓库 | star | 最后更新 | 用途 |
| --- | --- | --- | --- |
| `eth-lre/mathtutorbench` | 46 | 2026-08-27 | EMNLP 2025 Oral。**开放式教学能力**基准——测的不是答对率，而是「教得像不像好老师」，与你 T01–T18 判定维度同构，可借其评分维度 |
| `Khan/tutoring-accuracy-dataset` | 57 | 2024-08-29 | Khan Academy 论文配套数据，可校核 §13 引用的 Khanmigo 观察 |

star 都不高，但性质是学术评测集，价值不在社区规模，在于能给 42 条人工用例提供外部参照口径。

## 8. 中文小学场景补充件

| 仓库 | star | 许可证 | 最后更新 | 可复用点 |
| --- | --- | --- | --- | --- |
| `hezkvectory/hermes-edu-skills` | 128 | MIT | 2026-05-21 | **170 个中文教育 Skill，Hermes 技能包格式** |
| `Zenglian990/AI_Tutor_Release` | 77 | MIT | 2026-10-30 | 国内 1–12 年级**人教版分册分年级知识库**组织方式、LanceDB、FSRS 排期、「费曼同桌」（让孩子讲给 AI 听） |
| `SimonsTang/feifei-companion` | 110 | Apache-2.0 | 2026-04-19 | 家长侧设计可直接照搬：**每日简报／每周周报／家长沟通报告三种模板**、「第三单元不会」→ 自动定位到具体章节的话术 |
| `ZYT64/KuroTutor` | 4 | MIT | 2026-09-25 | 最贴近中国家庭实际路径：拍照 → 先给思路逐步引导 → 错题本按遗忘曲线重推；QQ 私聊接入 + 网页管理面板 |
| `hherb/primer` | 10 | AGPL-3.0 | 2026-10-30 | 唯一把「**能不答就不答**」写成硬规则的儿童项目；纯事实问题先直接答再反问延伸；local-first |
| `GeminiLight/gen-mentor` | 135 | CC0-1.0 | 2026-10-23 | WWW'25 ITS 官方实现，三 agent 分工可抄：Knowledge Gap Identifier → Learning Path Planner → Knowledge Drafter |
| `EasyRoc/edu-rag` | 59 | **无 LICENSE 文件** | 2026-10-18 | 检索工程最完整：Milvus Lite + BM25 + RRF 混合召回 + CrossEncoder 重排 + **检索门控**（低于阈值拒答，抑制幻觉）+ RAGAS 评估 |
| `GarethManning/education-agent-skills` | 935 | CC BY-SA 4.0 | 2026-10-22 | 165 个循证教育 skill（20 领域）。第 4 域「提问与对话」含 Socratic questioning / dialogic moves / hinge questions，可抄成中文版 |
| `CaviraOSS/PageLM` | 2,057 | 自定义社区许可 | 2026-10-29 | NotebookLM 式：教材／PDF → 笔记／闪卡／带提示的测验；`modules/` 里 quiz 的 hint + explanation 分层结构 |
| `HugeCatLab/ChatTutor` | 1,317 | AGPL-3.0 | 2026-01-09 | **Math Canvas / 白板**——小学生看「边画边讲」远胜纯文本；模型层已抽象 `AGENT_MODEL_PROVIDER`（含 deepseek），换国产模型零改代码 |
| `lixiang1076/kid-tutor` | 2 | MIT | 2026-02-26 | 6–12 岁：人教版 1-6 知识图谱 + 苏格拉底话术 + 家长报告脚本 |
| `dhjz/hanzi-study` | 240 | MIT | 2026-09-10 | 识字／笔画／听音识字／古诗朗读的现成交互与素材 |
| `tjsky/pinyin-annotator` | 415 | MIT | 2026-10-31 | 课文／绘本一键注音，纯前端离线（低年级适用） |

### 关于 hermes-edu-skills 的实测评价

**优点**：结构规整，是真 Hermes Skill 包（frontmatter 带 `metadata.hermes`），MIT，场景目录几乎 1:1 覆盖你的六 Skill 设计：

| 你的模块 | 它对应 |
| --- | --- |
| homework-help | `agent-homework-companion`、`agent-photo-question`、`agent-question-explanation` |
| 不直接给答案 | `agent-socratic-tutor`、`agent-mistake-review` |
| parent-review | `agent-learning-report`、`agent-weekly-review`、`agent-parent-companion` |
| reading-companion | `family-reading-companion`、`primary-reading-daily` |
| 教材同步 | `primary-math-rj-`（人教数学）、`primary-chinese-tongbian-`（统编语文）、`primary-english-pep-`（人教PEP英语） |

**但必须如实说**：抽查 `agent-homework-companion`、`agent-socratic-tutor`、`agent-learning-report`、`agent-photo-question`，每个都是 **约 4.6KB 的统一模板**（问题／最适合／不适合／使用前准备／推荐工作流／输出格式），教学法只有一句「卡住时给提示而非答案」这种陈述，**没有 hint ladder、没有证据 schema、没有可执行判定**。且 frontmatter 里 `requires_tools: [context.load, workflow.create, practice.generate_items, memory.write...]` 依赖一套外部 workflow 运行时，普通 Hermes 装上去跑不出它描述的流程。

**结论：当「场景目录 + 话术起点」用，不当教学引擎用。** 真正的引擎是 OATutor 那种代码实现。

## 9. 建议路径

**第 0 步（本周，零成本）**
拉 `cn-math-taxonomy` 的 `topics.json` + `questions.json`，查小三／小五段覆盖度（预期分别约 268 / 281 个知识点）。这是唯一能直接拿数据判断「够不够用」的一步。同时读 `diagnose/` 看先修边回溯怎么做的。

**第 1 步（与原计划并行，不冲突）**
WorkBuddy 双账号验证照 §8 走 D1（G01–G10）。成本低、能最快拿到孩子真实反应，不因引入新东西而推迟。

**第 2 步（关键决策点）**
决定「自建网页」之前，先花半天 Docker 起一个 DeepTutor，用虚构资料跑四项：
- learner/guardian 双账号是否符合 §3 与 G05
- Memory Graph 的证据链形态是否够当 §12.4 家长周报的来源
- shared Books 私有学习状态是否满足 T23
- 中文界面与本地化质量

能过，§15.4 网页路线的大头工程就省掉了，精力全部押在教学法策略层——**那才是你真正的差异化**。

**第 3 步（无论走哪条路都要做）**
- `promptfoo` 把 T01–T42 变成回归测试集
- `presidio` 落库前脱敏
- `mem0`（或 DeepTutor 自带记忆层）把 child_id 做成硬约束 + 回归测试
- OATutor 的 BKT 思路替掉模型自评掌握度
- `learning-commons/evaluators` 给 AI 讲解打适龄／课标对齐分，作为家长端可复核的第三方证据

## 10. 三个方向上都判定「必须自建」的部分

调研结论中最有价值的一条负向证据：**下面三项在 GitHub 教育生态里没有现成实现**，全部教育类仓库都是单学生模型。

| 缺口 | 现状 | 建议 |
| --- | --- | --- |
| 中文小学作文批改 | 只有课程级 Demo 和雅思方向（`MaFlamingo/AI-Intelligent-Homework-Grading-System` 5★ 是唯一能跑的中文 Demo） | 若要做，自己搭评分维度 JSON + 过程分 |
| 家长可查的学习证据链 | 无人做。`kid-tutor` 的家长报告最接近，但只有汇总数字 | 自建：`child_id + 事件表(ask/attempt/hint_used/verdict) + 家长只读视图` |
| 多孩子档案隔离 | 全部项目都是单 `User` | 同上，child_id 硬约束 + 跨 child_id 检索必须报错的回归测试 |

这三件正好是你方案的核心。**这说明方向是对的：不是重复造轮子，是填空白。**

## 11. 与现有方案的冲突点（需你判断）

1. **§13 提到的 Mr.-Ranedeer-AI-Tutor**（29,548★）现已在 README 标注 **DISCONTINUED**，纯 prompt 项目，只作历史参考，不作长期依赖。
2. **§15.4 假定「网页形态要从零建」** —— DeepTutor 的存在让这个假定需要重估。但引入它也意味着接受一个远超需求的大系统，与「不做 all-in-one」的偏好存在张力。
3. **cn-math-taxonomy 是 CC BY-NC** —— 家庭自用无碍，商业化路线需重估。
4. **`EasyRoc/edu-rag` 无 LICENSE 文件** —— 法务上不可直接用于对外产品。

## 12. 数据可信度声明

所有 star／许可证／最后提交时间均为 2026-11-01 通过 GitHub REST API 实测，非记忆值。
**未实测项**：各项目实际运行体验、中文教材版本覆盖精确度、DeepTutor 在儿童场景下的稳定性、hermes-edu-skills 在普通 Hermes 环境能否跑通其 workflow。这些必须实跑验证，不能凭 README 声明判定通过——与本方案 G01–G10「官方说明不能填通过」同一原则。
