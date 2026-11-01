# 开源项目选型：能给「沫沫与一一的学习伙伴」补什么

日期：2026-11-01。数据来源：GitHub REST API 实测（`repos/{owner}/{repo}`、`search/repositories`），star／许可证／最后提交均为当日实测值。
对应文档：[完整方案](final-plan-2026-10-27.md)、[工程规格](engineering-plan-2026-10-27.md)。

## 0. 一句话结论

**你的方案不缺设计，缺的是三样工程件：可靠的身份与记忆隔离、可机器判定的学习证据、客观掌握度算法。**
GitHub 上已有成熟开源件能补齐这三块；其中 `HKUDS/DeepTutor` 已实现你 §16.4 设想的「网页形态」大部分基础设施，值得在自建之前先评估。

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

它自称「Lifelong Personalized Tutoring」——终身个性化辅导工作台。关键是与本方案的重合点：

| 本方案的硬需求 | DeepTutor 已有能力 | 对应章节 |
| --- | --- | --- |
| 孩子/家长两种角色、家长单独空间 | v1.6.3 起有 **learner / guardian accounts** | §3、§5.4 |
| 两个孩子档案互不可见 | v1.4.3 起「real per-user isolation」；Workspaces 分离主题文件与学习状态 | §5.2、G05 |
| 家长看到「有据可查」的证据 | **Inspectable memory：L1 traces / L2 facts / L3 synthesis + Memory Graph 可审计证据链** | §12.1、§12.4 |
| 更正、忘记、撤回 | 记忆可编辑；归档会话可永久删除；回收站 | §5.4、T32、T35 |
| 一本共有书、两人状态不同 | v1.6.0 **shared Books with private learning state** | T23 |
| 记忆有边界、不无限膨胀 | v1.6.15 **bounded tutoring memory** | G04、§5.5 |
| 纸题拍照进电脑 | MinerU 解析接受 PDF／图片／DOCX／PPTX／XLSX；图片可送视觉模型 | §6.1 |
| 语音输入 | Voice 分组含转写与合成；支持小米 MiMo、MiniMax 等 | §6.1 |
| 家里的书进入伙伴 | Books／Reading／EPUB 标注／知识库（LlamaIndex、PageIndex、GraphRAG、LightRAG） | §9.1、§16.3 |
| 掌握度路径 | **Mastery Path** 模式，按工具分级 | §7.7 |
| 中文 | v0.6.0 起完整中文本地化；有微信／飞书社群 | — |
| 部署门槛 | `docker run` 一条命令；或 `pip install "deeptutor[full]"`（Python 3.11–3.14 + Node 20.9+）；或有 **Open DeepTutor 桌面安装包**（自带 Python 与 Node，免终端） | §15.4 |

**注意事项（实话）：**

- 它是个大系统，功能面远超本项目需要；上手成本和长期维护都要按实际情况估，不要按「装完就能用」理解。
- 它的教学法是通用型，不含「小学生不代做作业」这一层。你方案 §7 的**可跳级帮助方式**、§12 的**证据口径**仍然是你独有的、必须自己做的部分。
- 迭代极快（几乎每周发版），意味着**不要跟随 main 分支**；评估时钉住一个 release tag，记下版本号。
- Apache-2.0 允许商用改造，但二次分发时需保留声明。

## 2. 中文课标对齐：cn-math-taxonomy

| 项 | 值 |
| --- | --- |
| 仓库 | `xiaoyang111222/cn-math-taxonomy` |
| star | 5,655（fork 1,450） |
| 语言 | Python |
| 许可证 | **CC BY-NC 4.0（署名—非商业）** |
| 最后提交 | 2026-10-31 |

内容：数学（小学到高中）、英语（三年级到高中）、初中物理的知识图谱——**1644 个知识点、2403 条先修边、12,135 道题**（`questions.json` 实测条数，README 记 6723），对齐课标，附自适应前置诊断。

数据文件（实测）：

| 文件 | 大小 | 用途 |
| --- | --- | --- |
| `data/topics.json` | 2.6 MB | 知识点节点 |
| `data/dependencies.json` | 880 KB | 先修关系边（定位卡点、判断该不该讲下一层） |
| `data/cn-curriculum-standards.json` | 324 KB | 课标对齐 |
| `data/questions.json` | 7.8 MB | 题目 |

题目单条结构（实测样例）：

```json
{"difficulty":"basic","type":"numeric","prompt":"3 的后面一个数是几？",
 "answer":"4","explanation":"从 1 往后数，3 的后面是 4。",
 "verify":"3+1","id":"cnm_p001_q1","topicId":"cnm_p001"}
```

三个字段对本方案是实质升级：

1. **`topicId`** → 直接作为 `learning_event` 里的「具体概念标签」，不用模型自由生成标签。
2. **`explanation`** → 分层提示的取材来源。你 §7.2 的可跳级帮助需要「有真实表示／示范」，这是现成素材，且来源可标。
3. **`verify`** → **可执行验证式**。这一条最重要：你 §5.1 写「模型判断不是事实来源本身」，有了它，对错可以机器判定，不用模型自评。`performance` 字段（correct／incorrect）因此有了客观依据。

**许可证限制：** CC BY-NC 4.0 是**非商业**授权。自家孩子用没有问题；但若日后想产品化（你在 §15 里提到过长期路线），这一层要重新评估或自建题库。这不影响本阶段使用，但需要现在就记下来。

## 3. 教学目标与掌握度算法

| 仓库 | star | 语言 | 许可证 | 最后更新 | 可复用点 |
| --- | --- | --- | --- | --- | --- |
| `CAHLR/OATutor` | 274 | JS | MIT | 2026-10-31 | 卡内基梅隆开源智能辅导系统。**BKT（贝叶斯知识追踪）** 每知识点维护掌握概率；数据结构层面用 `giveHintOnIncorrect` 在答错时强制进提示路径而非重问。 |
| `plastic-labs/tutor-gpt` | 933 | TS | GPL-3.0 | 2026-02-20 | MemGPT 团队作品，用**心理理论（Theory-of-Mind）推理**判断学生当前状态再决定支持方式 |
| `HugeCatLab/ChatTutor` | 1,317 | Vue | AGPL-3.0 | 2026-01-09 | 可视化交互式 AI 家教 |
| `ECNU-ICALK/EduChat` | 975 | Jupyter | 无许可证 | 2025-07-18 | 华东师大开源中英教育对话大模型（通用基座，GPU 部署，商用前需确认授权） |
| `sunflower0305/ai-kid-tutor` | 31 | Python | 自定义 | 2026-04-03 | 核心原则与本方案完全一致：**永不直接给答案**，只反问。代码量小，适合读它的提示设计，不适合当基座 |
| `AnkitClassicVision/tutor-engine` | 3 | TS | AGPL-3.0 | 2026-10-22 | 面向 5–14 岁儿童与家长；「mastery from independent work」（**独立作答才算掌握**）+ 每家庭加密。概念与 T29 高度一致，但项目极小、未经验证 |

**最重要的一条工程启发**（来自 OATutor）：
把「不直接给答案」从提示词祈求，改为**数据结构保证**——答错时状态机自动进入提示路径，而不是每次靠模型自觉。这直接加强你 §7.2 与 T02／T05／T06 的可靠性。

**第二条启发**（BKT）：
你 §5.1 里 `performance` 与「掌握」目前只靠模型判断。BKT 给出的是可计算的掌握概率，可以作为一个独立于模型自评的证据来源，正好补上「模型判断不是事实来源本身」这句的自相矛盾之处。

## 4. 学习证据链（家长周报的底层）

| 仓库 | star | 语言 | 许可证 | 最后更新 | 用法 |
| --- | --- | --- | --- | --- | --- |
| `adlnet/ADL_LRS` | 334 | Python | Apache-2.0 | 2025-11-14 | ADL 官方 xAPI Learning Record Store，对齐 IEEE 9274.1.1（xAPI 2.0）。**证据链存储层**：每次练习／对话产出一条 statement，家长端只读 statement，不由模型复述 |
| `learningequality/kolibri` | 1,163 | Python | MIT | 2026-11-01 | 面向 K-12 的离线学习平台。抄它的 **coach 视图数据模型**（每 learner × 每 exercise 掌握度），不抄技术栈 |
| `oppia/oppia` | 6,951 | Python | Apache-2.0 | 2026-10-31 | 按 learner 记录显式学习状态与目标。参考 `learner_goals` 这类显式状态表，**避免用 LLM 生成「学习报告」** |
| `openedx/openedx-platform` | 8,213 | Python | AGPL-3.0 | 2026-10-31 | 参考 `track` 事件表结构（谁／何时／哪个知识点／结果）做埋点设计 |
| `instructure/canvas-lms` | 6,893 | Ruby | AGPL-3.0 | 2026-04-30 | 参考 outcome → rubric → mastery 的口径定义 |

**不建议引入 Canvas / Open edX 本体**：AGPL + 运维成本，两个孩子用不上，只借数据模型。

## 5. 记忆隔离（当前 WorkBuddy 最大的不确定项）

| 仓库 | star | 许可证 | 最后更新 | 用法 |
| --- | --- | --- | --- | --- |
| `mem0ai/mem0` | 68,172 | Apache-2.0 | 2026-10-30 | 源码级支持 `user_id` / `agent_id` / `run_id` 三元作用域。child_id 直接当 user_id，agent_id 固定 tutor，所有检索强制带 filter |
| `topoteretes/cognee` | 32,966 | Apache-2.0 | 2026-10-30 | 显式 multi-tenant 模式 + dataset 级隔离，每孩子一个 dataset |
| `getzep/graphiti` | 32,400 | Apache-2.0 | 2026-11-01 | 按 `group_id` 硬分区；README 明说 MCP server 不鉴权，须自己加 |
| `letta-ai/letta` | 25,310 | Apache-2.0 | 2026-10-18 | agent-per-child 天然隔离（memory blocks） |
| `MemTensor/MemOS` | 12,209 | Apache-2.0 | 2026-10-29 | 「memory cube」支持隔离与受控共享，可做「家庭共享知识 + 孩子私有记忆」两层 |
| `getzep/zep` | 4,984 | Apache-2.0 | 2026-11-01 | user / thread 两级，经典方案 |

## 6. 儿童安全护栏与回归测试

| 仓库 | star | 许可证 | 最后更新 | 用法 |
| --- | --- | --- | --- | --- |
| `promptfoo/promptfoo` | 26,679 | MIT | 2026-10-31 | **把 T01–T42 变成可回归的测试集**。每次改提示词跑一遍，防止改坏。这是你 §7 验收矩阵的自动化路径 |
| `data-privacy-stack/presidio` | 11,615 | MIT | 2026-10-31 | 落库前 PII 脱敏：姓名／学校／住址／电话不进记忆库与日志，对应 T30 |
| `NVIDIA/garak` | 9,814 | Apache-2.0 | 2026-10-27 | LLM 漏洞扫描（越狱／泄露／幻觉），上线前扫一遍，产出可给家长看的安全报告 |
| `guardrails-ai/guardrails` | 7,575 | Apache-2.0 | 2026-10-31 | 输出侧 schema 校验，防止模型编造「已完成／已掌握」，对应 §5.3「失败不假成功」 |
| `NVIDIA-NeMo/Guardrails` | 7,403 | Apache-2.0 | 2026-10-30 | 可编程对话护栏：定义「小学生模式」话题域与兜底答复 |
| `meta-llama/PurpleLlama` | 4,455 | Llama Community（非 OSI） | 2026-10-30 | Llama Guard 做儿童内容分类；Prompt Guard 挡注入（孩子一定会乱试），对应 T37 |
| `unitaryai/detoxify` | 1,312 | Apache-2.0 | 2026-10-20 | 轻量毒性打分兜底 |

已排除：`protectai/llm-guard` 3,220★ 已 **archived**（2026-07-08），新项目不要引入。

## 7. 评测基准（把「教得好不好」变成可测）

| 仓库 | star | 最后更新 | 用途 |
| --- | --- | --- | --- |
| `eth-lre/mathtutorbench` | 46 | 2026-08-27 | EMNLP 2025 Oral。**开放式教学能力**评测基准——测的不是答对率，而是「教得像不像好老师」。与你 T01–T18 的判定维度同构，可借用其评分维度 |
| `Khan/tutoring-accuracy-dataset` | 57 | 2024-08-29 | Khan Academy 论文配套数据，「LLM 数学辅导的挑战与数据集」。可校核你 §13 引用的 Khanmigo 观察 |

这两个 star 都不高，但性质是**学术评测集**，价值不在社区规模，在于能给你的 42 条人工用例提供外部参照口径。

## 8. 建议路径

**第 0 步（本周，零成本）**
把 `cn-math-taxonomy` 的 `topics.json` + `questions.json` 拉下来，检查小学三年级／五年级段的覆盖度。这是**唯一能直接拿出数据判断「够不够用」**的一步。同时读它的 `diagnose/` 目录看前置诊断怎么做的。

**第 1 步（与你原计划并行，不冲突）**
WorkBuddy 双账号验证照原计划走 D1（G01–G10）。这一步成本低、能最快拿到孩子真实反应，且不因引入新东西而推迟。

**第 2 步（关键决策点）**
在决定「自建网页」之前，**先花半天用 Docker 起一个 DeepTutor 实例**，用虚构资料跑一遍：
- 家长/孩子双账号是否真的符合你的 §3 与 G05
- Memory Graph 的证据链形态是否够当作 §12.4 家长周报的来源
- shared Books 的私有学习状态是否满足 T23
- 中文界面与本地化质量

如果这四项能过，你 §15.4 的「网页路线」工程量大头就被省掉了，你可以把精力全部放在**教学法策略层**（这才是你真正的差异化）。

**第 3 步（无论走哪条路都要做）**
- 用 `promptfoo` 把 T01–T42 变成回归测试集
- 用 `presidio` 做落库前脱敏
- 用 `mem0`（或 DeepTutor 自带记忆层）把 child_id 隔离做成硬约束 + 回归测试
- 用 OATutor 的 BKT 思路，把「掌握」从模型自评换成可计算量

## 9. 与现有方案的冲突点（需要你判断）

1. **§13 提到 Mr.-Ranedeer-AI-Tutor 类提示工程思路** —— 该仓库（29,548★）现已在 README 标注 **DISCONTINUED**，纯 prompt 项目，不适合作为长期依赖，只作历史参考。
2. **§15.4 假定「网页形态要从零建」** —— DeepTutor 的存在让这个假定需要重新评估。但反过来，引入它也意味着你要接受一个远超需求的大系统，这与「不做 all-in-one」的偏好存在张力。
3. **cn-math-taxonomy 是 CC BY-NC** —— 家庭自用无碍，商业化路线需重估。

## 10. 数据可信度声明

本文件所有 star／许可证／最后提交时间均为 2026-11-01 通过 GitHub REST API 实测，非记忆值。
未实测项：各项目的实际运行体验、中文教材版本覆盖精确度、DeepTutor 在儿童使用场景下的稳定性。这些需要按第 8 节第 2 步实跑验证，不能凭 README 声明判定通过——与本方案 G01–G10「官方说明不能填通过」的同一原则。
