# 交接文档（HANDOFF）· 给 Codex 的续作指南

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

- `workbuddy/PROJECT_INSTRUCTIONS.md` — 项目常驻指令（教学约定 + 身份边界 + 记忆规则）。
- `workbuddy/skills/` — 4 个 Skill：`homework-help`（作业卡点）、`explore-task`（探索创作）、`learning-log`（学习证据记录）、`parent-review`（家长周报，仅家长入口）。
- `profiles/*.example.json` — 沫沫/一一示例档案（虚构字段，正式档案不入库）。
- `schemas/learning-event.schema.json` — 学习事件格式（jsonl）。
- `validation/prototype-checklist.md` — 部署后的验收清单（P0 隔离/持久/教学行为，P1 体验/记录/试用观察）。
- `workbuddy/README.md` — 部署步骤与平台边界提醒。

### 第二轮推进（2026-10-26 傍晚，Kimi Work 基于家长提供的全部 Codex 原始提示词）

- 家长补齐了全部历史提示词，其中最后一条（网页版 vs WorkBuddy 的路线问题）是 Codex 中断前未回答的问题。
- 教材核实（家长确认"三科应为人教版"后逐科查证）：
  - 语文 = 统编教材（人教社），全国统一，可确认。
  - 英语 = 重庆有人教 PEP / 重大版 / 外研版并存，大概率人教 PEP 新教材，待课本封面确认系列与册次。
  - 数学 = **重庆人教版与西师版（西南大学出版社）并存**，家长记忆对数学可能不准确，必须实物核对封面与版权页。
- 路线决策已作出并成文：`notes/tech-route-decision-2026-10-26.md`——**采用自建网页版为正式形态**（可控性强：双账户隔离、教学规则后端强制、数据私有、拟人化界面），WorkBuddy 并行小成本验证教学对话；含推荐架构（React + FastAPI + OpenAI 兼容模型接口 + 分账户 jsonl 学习库）。
- 两个示例档案按家长描述更新（教材置信度、兴趣、家长观察），仍保持昵称制、不含姓名生日。
- 家长原始提示词已归档到 `notes/codex-prompts-archive-2026-10-26.txt`（含姓名生日，已 gitignore，不进仓库）。

### 本仓库

- GitHub 私有仓库（账号 18523102883hao-boop），工作区即仓库根目录（iCloud 路径 `/Users/Zhuanz/Library/Mobile Documents/com~apple~CloudDocs/学习助手`）。

## 3. 当前停在什么位置

- **Codex 中断点**：会话 2 在做一手来源补充调研（DragonBox 研究、隐私条款页）时额度耗尽。四份 notes 均已保存，**没有半截文档需要续写**。
- **项目所处阶段**：调研/设计已收尾，原型配置草案刚由 Kimi Work 产出，**尚未部署到 WorkBuddy，未做任何实测**。

## 4. 建议的下一步（按优先级）

1. **搭建网页版 MVP**（路线已定，见 `notes/tech-route-decision-2026-10-26.md`）：需要先向家长确认三件事——①订阅的模型提供商与可用的多模态模型（配 base_url/api_key 与拍题识别）；②后端先跑哪台电脑；③儿童端形象偏好。确认后即可开工：React 儿童端（语音/拍照/帮助按钮）+ FastAPI 后端（账户、教学引擎、学习事件、周报）+ 复用现有 PROJECT_INSTRUCTIONS 与 4 个 Skill 内容。
2. **家长拍数学课本封面+版权页**（语文已确认为统编版；英语大概率人教 PEP 也一并拍）——重庆数学人教版/西师版并存，这是目前最大的版本风险点。确认后把 curriculum 置信度提升并绑定单元讲解。
3. **WorkBuddy 快速验证**（可选、并行）：用现有配置草案跑几天教学对话，验证孩子是否愿意用、提示节奏是否合适，结论回流入网页版。
4. **两周家庭试用**：从一个共同的数学卡点 + 每人一个自选探索任务开始；观察清单见 `validation/prototype-checklist.md` P1 部分。
5. **视试用结果决定**前端与教学规则的迭代方向。

## 5. 工作约定（沿用家长与 Codex 的约定）

- 默认简体中文；代码、命令、路径不翻译。
- 不替孩子做作业是硬红线；任何新功能先问"这会否变成代做/贴标签/姐妹比较"。
- 教育表述要有依据：未经证实的比例、留存率不写成参数；"两次未推进换讲法"等是初始假设，由试用校准。
- 家长报告只写有证据的内容，人格/动机结论永不输出。
- 孩子的完整姓名、生日不进仓库；真实档案 `.gitignore`。

## 6. 文件地图（速查）

```
README.md                        项目总览
HANDOFF.md                       本文档
notes/                           调研与设计（5 份）
workbuddy/
  README.md                      部署步骤
  PROJECT_INSTRUCTIONS.md        项目常驻指令
  skills/{homework-help,explore-task,learning-log,parent-review}/SKILL.md
profiles/                        示例档案 + 说明
schemas/learning-event.schema.json
validation/prototype-checklist.md
```

## 7. 外部资源

- 教育知识库（家长本地，未入库）：`/Users/Zhuanz/Documents/Obsidian Vault/knowledge/parenting-agent-kb`（113 份转录 + 113 张策略卡；字段不一致，选用前需做字段统一与来源回查，见设计稿 §8）。
- Codex 原始会话：`~/.codex/sessions/2026/10/26/`。
