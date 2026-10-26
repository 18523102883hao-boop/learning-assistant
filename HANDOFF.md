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

### 本仓库

- GitHub 私有仓库（账号 18523102883hao-boop），工作区即仓库根目录（iCloud 路径 `/Users/Zhuanz/Library/Mobile Documents/com~apple~CloudDocs/学习助手`）。

## 3. 当前停在什么位置

- **Codex 中断点**：会话 2 在做一手来源补充调研（DragonBox 研究、隐私条款页）时额度耗尽。四份 notes 均已保存，**没有半截文档需要续写**。
- **项目所处阶段**：调研/设计已收尾，原型配置草案刚由 Kimi Work 产出，**尚未部署到 WorkBuddy，未做任何实测**。

## 4. 建议的下一步（按优先级）

1. **等家长提供教材照片**：核对语文/数学/英语版本与系列（重庆主城区；英语若是人教版需辨 PEP/精通）。确认后填入 `profiles/*.json` 的 `curriculum`，助手才能绑定单元与词汇表。在此之前只做跨版本概念辅导。
2. **部署 WorkBuddy 原型**（步骤见 `workbuddy/README.md`）：建项目 → 粘贴常驻指令 → 导入 4 个 Skill → 放虚构示例档案 → **关闭未验证的自动记忆**。
3. **跑验收清单**（`validation/prototype-checklist.md`）：先用虚构档案做 P0 隔离与持久测试，全过后才换真实（去标识）档案。
4. **两周家庭试用**：从一个共同的数学卡点 + 每人一个自选探索任务开始（任务备选见 `explore-task` Skill）；观察清单见验收文档 P1 部分。试用数据回流后调整提示长度、节奏、帮助层级。
5. **视试用结果决定**：继续 WorkBuddy 深化，或按设计稿 §7 评估腾讯云 ADP / Dify（需要固定儿童界面、身份锁定时）。

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
