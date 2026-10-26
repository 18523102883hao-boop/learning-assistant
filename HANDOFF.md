# 交接文档（HANDOFF）· 给 Codex 的续作指南

> **当前交接已更新（2026-10-27）：请先读 [v3交接](notes/development-handoff-2026-10-27.md)、[完整方案](notes/final-plan-2026-10-27.md)与[工程附录](notes/engineering-plan-2026-10-27.md)。** 用户要求先审阅详细综合方案，确认后再开发。最新Kimi与家庭决定已纳入，仍未制作正式运行配置或实测产品。以下历史“定稿/第一件事独立赛马/立即部署”不能覆盖当前范围；文档在GitHub可读不等于实现已获授权。

## 以下为历史交接记录

> 更新日期：2026-10-26（Kimi Work 整理并推进）
> 背景：家长原用 Codex 开发本项目，2026-10-26 15:11 左右 Codex 额度耗尽中断。本仓库由 Kimi Work 在中断点基础上建立，Codex 额度恢复后请从本文档继续。

## 1. 项目一句话

为两个女儿（姐姐沫沫·五年级、妹妹一一·三年级）做引导式学习助手：**不直接给答案，逐级引导；为家长产出有证据的学习摘要；让孩子体验学科的意义与乐趣**。首选腾讯 WorkBuddy 做原型。

## 2. 已完成（截至 2026-10-26）

### 调研与设计（notes/，四份文档已完整，无中断残留）

- `learning-assistant-design-draft.md` — 整体方案：三个入口、教学规则、家长视图、记忆与隔离、技术路线、教材核验、两个孩子的个性化设计。
- `education-principles-and-engagement-design.md` — 教育理念→交互规则；含对"85%规则/学习金字塔"等表述的校准。
- `learning-tools-best-practices-2026-10-26.md` — Khanmigo、DragonBox、Duolingo、学而思、讯飞学习机、小度的可借鉴机制与证据边界。
- `workbuddy-platform-research-2026-10-26.md` — WorkBuddy/ADP/Dify 一手资料核验，含未确认项清单。
- `session-log-2026-10-26.md` — 当天两个 Codex 会话的经过与中断点。

### 原型配置（Kimi Work 本次新增，把设计落成可部署草案）

- 原始草案已升级并按赛马机制归档为 **Kimi 版 v1.0**（`workbuddy/kimi/`，见下）。
- 其余共享地基（两版通用，不属于任何一方）：`profiles/*.example.json`（沫沫/一一示例档案，虚构字段，正式档案不入库）、`schemas/learning-event.schema.json`（学习事件 jsonl 格式）、`validation/prototype-checklist.md`（部署后验收清单 P0/P1）、`workbuddy/README.md`（部署步骤、平台边界、赛马规则）。

### 第六轮 · 赛马机制与 Kimi 版 v1.0（2026-10-26 深夜，家长决定）

- **家长启用赛马**：Kimi 与 Codex 各写一版 WorkBuddy 配置，家长评比后由 Codex 综合出最终版。规则与目录结构见 `workbuddy/README.md`。
- **Kimi 版 v1.0**（`workbuddy/kimi/`）：按方案 v1.0 + 修订②编写，含——
  - `PROJECT_INSTRUCTIONS.md`：平等伙伴身份、教学约定（含第 0 级情绪接收）、**语言 lint**（禁人格/天赋评价词）、冷启动剧本、注意力护栏、场景分布、**五个入口**；
  - 6 个 Skill：homework-help（情绪接收+四级帮助+跳级+迁移验证）、explore-task、**partner-chat（新增：伙伴闲聊，五条红线+收口护栏）**、**reading-companion（新增：阅读伙伴——引读家中存书/推荐新书/图文→纯文字过渡陪读/4F 聊读后感/买书跟进闭环，书架库 `schemas/bookshelf.schema.json`）**、learning-log（新增 scene_type 场景分类，闲聊只记次数）、parent-review（新增场景分布行 + **周报落 Markdown 文档**）；
  - 已体现 §8 家长决议：口语跟读与整页对答案 v1 不做、周报落文档、使用约定待家长线下确定。
- **v1.0 修订③（家长 19:04）**：阅读伙伴成为家长第一优先级之一（方案新增 §3C-附）。家长将上传书架实拍建书目库、陆续提供认可的书籍与课程（首批：刘擎《西方现代思想讲义》，存 `library/parent-materials/`，已 gitignore，入库的只有提炼要点）。
- `workbuddy/codex/`（空目录，Codex 写自己的版本）；`workbuddy/final/`（空目录，Codex 综合产出）。

### 第二轮推进（2026-10-26 傍晚，Kimi Work 基于家长提供的全部 Codex 原始提示词）

- 家长补齐了全部历史提示词，其中最后一条（网页版 vs WorkBuddy 的路线问题）是 Codex 中断前未回答的问题。
- 教材核实（家长确认"三科应为人教版"后逐科查证）：
  - 语文 = 统编教材（人教社），全国统一，可确认。
  - 英语 = 重庆有人教 PEP / 重大版 / 外研版并存，大概率人教 PEP 新教材，待课本封面确认系列与册次。
  - 数学 = **重庆人教版与西师版（西南大学出版社）并存**，家长记忆对数学可能不准确，必须实物核对封面与版权页。
- 路线决策已作出并成文：`notes/tech-route-decision-2026-10-26.md`——**采用自建网页版为正式形态**（可控性强：双账户隔离、教学规则后端强制、数据私有、拟人化界面），WorkBuddy 并行小成本验证教学对话；含推荐架构（React + FastAPI + OpenAI 兼容模型接口 + 分账户 jsonl 学习库）。
- 两个示例档案按家长描述更新（教材置信度、兴趣、家长观察），仍保持昵称制、不含姓名生日。
- 家长原始提示词已归档到 `notes/codex-prompts-archive-2026-10-26.txt`（含姓名生日，已 gitignore，不进仓库）。

### 第三轮修订（2026-10-26 晚，方案 v0.2）

- 家长拍板：**WorkBuddy 双账户先行落地**（两个孩子各用自己的手机号注册独立账号，一人一个学习项目），网页版降级为长期备用路线（触发条件写入方案 §6 Phase 3）。
- 理由与核实结果：拍照/语音是孩子刚需（现用 DeepSeek 拍题问作业）且为 WorkBuddy 现成功能；手机号注册双账号可行，免费版每人 500 积分/月可能零成本跑试用，不足时标准版 70 元/月/账号。
- 新增 `notes/learning-machines-deep-research-2026-10-26.md`：讯飞全产品线（T90 Pro/T30 Pro/S90 Pro/启蒙线）与"学情诊断—路径规划—动态干预"交互闭环拆解、可借鉴点（步骤级诊断、掌握度可视化、变式练习、超拟人老师）与不借点（诊断标签化、刷题导向），附到店实机体验清单。
- 方案主文档更新为 v0.2：`notes/master-proposal-2026-10-26.md`。
- **开发仍然未启动**：方案 v0.2 供家长逐条讨论，定稿为 v1.0 后才进入 WorkBuddy 部署阶段。

### 第四轮修订（2026-10-26 晚，方案 v0.3 → v0.5，Kimi Work）

- 家长提出两个新维度并逐轮修正：**孩子视角审查**（§3A，8 个缺口，最重要修正=先兴趣后作业的冷启动剧本）与 **AI 学习助手产品经理视角审查**（§3B，北极星=7 日回访率+无辅助迁移率，MVP 收敛为单入口，分阶段启动）。
- 家长提出第四入口**伙伴模式**（"随便聊聊"）：沫沫已在用 DeepSeek 聊猫小九。定位经家长修正为**平等伙伴**（非粉丝非老师）；四条红线；家长端默认摘要可见性。
- 教材结论维持：语文统编已确认；英语大概率人教 PEP 待确认；数学必须实物核对。
- 方案主文档：`notes/master-proposal-2026-10-26.md`（v0.5）。

### 第五轮修订（2026-10-26 深夜，方案 v1.0，Kimi Work）

- **完成《新父母大学》五门课全部原文通读**（约 90 讲：c1 成就孩子 / c2 自主学习力 / c3 带孩子阅读 / c4 积极心理学 / c5 高情商沟通），提炼落盘于工作区 `references/kb-distill/c1–c5.md`（该目录已 gitignore，不进仓库；若需原文引用可回查家长本地知识库 `parenting-agent-kb`）。
- **§3C 伙伴思维体系从 10 条扩为 22 条全集**，按六组编排（关系根基/对话方式/成长内核/学习方法/品格视野/特色游戏），每条标注课程与讲次来源——这是 Codex 编写 Skill 提示词的方法论底座。
- §3A 增补缺口 9–12（情绪先于讲题的第 0 级流程、有效支持初衷校验、注意力时长定交互粒度、闲聊=情感账户存款）；§3B 增补 3 条（ACE 差异化内核、场景触发而非意志力、输出语言 lint 禁人格评价词）；帮助流程升为"第 0 级情绪接收 + 四级帮助"；附录新增场景 G（考砸后的习得性无助防护与支点科目策略）。
- **开发仍然未启动**：v1.0 是定稿候选，待家长逐条确认（开放问题见方案 §8）后转正式 v1.0 并进入 Phase 1。

### 本仓库

- GitHub 私有仓库（账号 18523102883hao-boop），工作区即仓库根目录（iCloud 路径 `/Users/Zhuanz/Library/Mobile Documents/com~apple~CloudDocs/学习助手`）。

## 3. 当前停在什么位置

- **Codex 中断点**：会话 2 在做一手来源补充调研（DragonBox 研究、隐私条款页）时额度耗尽。四份 notes 均已保存，**没有半截文档需要续写**。
- **项目所处阶段**：调研/设计已收尾，原型配置草案刚由 Kimi Work 产出，**尚未部署到 WorkBuddy，未做任何实测**。

## 4. 建议的下一步（按优先级）

> **⚠️ 家长已启用赛马机制（2026-10-26 17:54）**：Codex 恢复后，第一件事**不是**继续 Kimi 的方案，而是按下面第 0 步写出你自己的独立版本，然后综合。

**第 0 步 · Codex 写自己的版本（赛马上半场）**
- 在 `workbuddy/codex/` 下从零写你自己的版本：结构与 `kimi/` 相同（`PROJECT_INSTRUCTIONS.md` + `skills/homework-help, explore-task, partner-chat, reading-companion, learning-log, parent-review` 共 6 个 Skill）。
- **写之前不要读 `workbuddy/kimi/` 的任何文件**——赛马比的是原始判断，不是改写能力。你可以读 `notes/master-proposal-2026-10-26.md`（v1.0 方案，双方共同的输入）、`notes/` 下全部调研文档、`schemas/`、`profiles/`、`validation/`，这些是两版共享的地基。
- 写完后在 `workbuddy/codex/DESIGN-RATIONALE.md` 里说明你的关键设计决策及理由（不限于：身份定位、帮助层级、情绪处理、伙伴模式边界、记录粒度）。

**第 1 步 · Codex 综合最终版（赛马下半场）**
- 读 `kimi/` 版，与 `codex/` 版逐组件对比，提取双方优点合成 `workbuddy/final/`。
- 必须写 `workbuddy/final/CHANGELOG.md`：逐条注明每条规则的取舍来自哪一版（或两版融合）及理由；存在实质分歧且无法融合的，列出两版差异供家长拍板。
- 综合时不得丢失 v1.0 方案 §8 的家长决议（口语跟读与整页对答案 v1 不做、周报落 Markdown 文档、使用约定待家长线下确定）。

**第 2 步 · 部署与试用（综合版定稿后）**

> 路线现状（v0.2 起）：**WorkBuddy 双账户先行落地，网页版为长期备用路线**（触发条件见方案 §6 Phase 3，预研在 `notes/tech-route-decision-2026-10-26.md`）。以下步骤基于综合版定稿。

1. **Phase 1 WorkBuddy 双账户部署**（方案 §6）：两个手机号注册两个账号，各建学习项目，粘贴综合版 `PROJECT_INSTRUCTIONS.md`、导入综合版 Skill（先只启用 homework-help 与 learning-log）、放入去标识档案；按 `validation/prototype-checklist.md` P0 验收。
2. **Phase 1.5 冷启动周（姐姐先行 5–7 天）**：前 3 次对话按冷启动剧本（兴趣邀请→小任务→作业救急）；验证北极星指标信号后再启动一一。
3. **家长拍数学课本封面+版权页**（英语 PEP 一并拍）——数学人教版/西师版并存是当前最大版本风险点。
4. **Phase 2 两周家庭试用**：启用 explore-task、复述流程与伙伴模式；每周 30 分钟产品会复盘指标（7 日主动回访率、无辅助迁移率、首轮有效帮助延迟、帮助升级率、闲聊/学习场景分布）。
5. **Codex 综合时的注意事项**：§3C 伙伴思维体系 22 条（含讲次来源）是方案层的方法论底座，综合时可改写法但不得静默丢弃条目；§3B-11 语言 lint（禁人格/天赋评价词）与缺口 13 注意力护栏（一次收口/惯例表/自然后果）是家长明确确认过的设计，改动需在 CHANGELOG 中显式说明并给理由。

## 5. 工作约定（沿用家长与 Codex 的约定）

- 默认简体中文；代码、命令、路径不翻译。
- 不替孩子做作业是硬红线；任何新功能先问"这会否变成代做/贴标签/姐妹比较"。
- 教育表述要有依据：未经证实的比例、留存率不写成参数；"两次未推进换讲法"等是初始假设，由试用校准。
- 家长报告只写有证据的内容，人格/动机结论永不输出。
- 孩子的完整姓名、生日不进仓库；真实档案 `.gitignore`。

## 6. 文件地图（速查）

```
README.md                        项目总览
HANDOFF.md                       本文档（含赛马规则与 Codex 任务清单）
notes/                           调研与设计（含 master-proposal v1.0，赛马共同输入）
workbuddy/
  README.md                      部署步骤 + 赛马机制说明
  kimi/                          Kimi 版 v1.0（PROJECT_INSTRUCTIONS.md + 5 个 Skill）
  codex/                         Codex 版（待编写；写前先别看 kimi/）
  final/                         最终综合版（待 Codex 产出；含 CHANGELOG.md 取舍记录）
profiles/                        示例档案 + 说明
schemas/learning-event.schema.json
validation/prototype-checklist.md
```

## 7. 外部资源

- 教育知识库（家长本地，未入库）：`/Users/Zhuanz/Documents/Obsidian Vault/knowledge/parenting-agent-kb`（113 份转录 + 113 张策略卡；字段不一致，选用前需做字段统一与来源回查，见设计稿 §8）。
- Codex 原始会话：`~/.codex/sessions/2026/10/26/`。
