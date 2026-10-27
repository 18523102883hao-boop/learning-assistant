# WorkBuddy 专家包踩坑记录与账号搭建 Runbook

> 2026-10-27 全部实证总结（张一沫账号搭建过程中逐条验证）。给妹妹（张颖一）搭建时照此执行，可一次到位。
> 三个包的分支：`experts/learning-partner-momo`（伙伴 · 沫沫）、`experts/learning-partner-yiyi`（伙伴 · 一一）、`experts/learning-report-analyst`（成长手记，家长端）。

## 一、加载机制（全部经会话记录取证）

| # | 坑 | 实证 | 对策 |
|---|---|---|---|
| 1 | **专家只完整注入 `agents/<name>.md`** | 孩子问"你知道我的名字吗"答不出——包根 `profiles/*.json` 从不加载 | 关键内容（孩子小档案、人格、底线）必须写进 agent 文件本体 |
| 2 | `skills/*/SKILL.md` 不预载，按需触发 | 闲聊会话全程无 SKILL.md 注入 | 四种意图的底线全部在常驻指令里兜底，技能不触发也不裸奔 |
| 3 | `references/` 大文件（147 条书目 catalog.v3.json 等）Ask 模式不可达 | 该模式无任何文件读取工具 | 核心方法写进 SKILL.md 正文；大文件留待接工具阶段 |
| 4 | **版本号缓存机制**：marketplace 改动只在 version 变化时重新同步进 `plugins/cache/`；运行时用的是 cache 副本 | 多次改了文件不生效，bump version 后才同步 | 任何内容修改必须 bump version；紧急生效要同时改 cache 副本 |
| 5 | 需要同步的位置有三个 | 只改一处常常"看着改了但没生效" | **GitHub 分支 → marketplaces/my-experts/plugins/ → cache/my-experts/<name>/<ver>/** 三处一致 |
| 6 | `~/.workbuddy/memory/<uid>_memory.md` 是**云端管理**的 | 手动写入三次均被 app 覆盖（Version 重置为 0） | **不要手动写这个文件**；见下方稳定通道 |
| 7 | 稳定记忆通道是账号身份文件 | `~/.workbuddy/user-<uid>-personal/USER.md`、`IDENTITY.md` 每个会话都注入，不受云记忆覆盖 | 孩子的完整档案写这里 + agent 小档案，双保险 |
| 8 | **专家对话每次开新工作区文件夹**（按时间戳） | `projects/Users-Zhuanz-WorkBuddy-<时间戳>/` | 项目级记忆无法跨对话积累；跨会话延续靠第 7 条 |
| 9 | 两个孩子的包在同一台机器的市场里**并存可见** | 沫沫的会话误选了"伙伴 · 一一"，她把沫沫叫成了"张颖一" | 包名必须不同（learning-partner / learning-partner-yiyi）；显示名带孩子名；一一包 displayDescription 已加【一一专用，别选错】 |
| 10 | "从 GitHub 同步创建专家"会用分支内容**覆盖本地 marketplace** | 家长本地的显示名自定义差点丢失 | 本地自定义必须回写分支（1.1.5 已回写），保持 GitHub 是唯一源头 |
| 11 | 模型可能忽略已注入的 USER.md | hy3 声称"记忆小本本没名字"，但 USER.md 里明明有 | 档案在多处冗余是必要的；deepseek-v4.1-flash / hy3 表现有差异，测试时看实际回答 |
| 12 | `displayDescription.zh` 有长度约束 | 包测试断言 40–50 字 | 改展示语后跑 `tests/test_learning_partner_expert.py` |

## 二、给妹妹搭建的 Runbook（按序执行）

1. **登录一一的 WorkBuddy 账号**（这台电脑切换即可，插件市场是机器级共享的，两个包都已在市场里）。
2. **专家选择**：在她的对话里选 **"伙伴 · 一一"**（带【一一专用】标记）；确认没选成"伙伴 · 沫沫"。**"成长手记"绝不装在孩子账号**——它只装在你的账号。
3. **写身份档案**（最关键一步）：登录后 `~/.workbuddy/user-<新uid>-personal/` 会生成，把沫沫账号 `USER.md`/`IDENTITY.md` 改成一一版（三年级、人教版三门、手工/读书、丁雨彤）。注意 **不要**手动写 `~/.workbuddy/memory/<uid>_memory.md`，会被云覆盖。
4. **验证**：新开会话问"你知道我是谁吗"——应回答"知道呀，你叫一一（张颖一）……是爸爸告诉我的"；再问猫小九应该答不上来（那是对的，一一的档案里没有）。
5. **跨会话记忆测试**：聊一件具体小事 → 另开新会话问"我上次说到哪了"——验证记忆机制（此前未实测通过，若失败属平台限制，记录在案）。
6. **把她的显示名/自定义回写分支**，保持 GitHub 唯一源头。

## 三、文件位置速查（本机）

```
~/.workbuddy/plugins/marketplaces/my-experts/plugins/   ← 专家包源（市场目录）
~/.workbuddy/plugins/cache/my-experts/<name>/<version>/ ← 实际运行的缓存副本
~/.workbuddy/plugins/installed_plugins.json             ← 安装注册表（机器级）
~/.workbuddy/plugins/known_marketplaces.json            ← 市场注册
~/.workbuddy/user-<uid>-personal/USER.md|IDENTITY.md    ← 账号身份档案（稳定通道）
~/.workbuddy/memory/<uid>_memory.md                     ← 云管理记忆（勿手改）
~/.workbuddy/projects/<工作区>/<会话>.jsonl             ← 会话原文（可取证注入内容）
```

## 四、当前版本

- 伙伴 · 沫沫：v1.1.5（`experts/learning-partner-momo`，显示名已带 · 沫沫）
- 伙伴 · 一一：v1.0.2（`experts/learning-partner-yiyi`，带【一一专用】标记）
- 成长手记：v1.1.0（`experts/learning-report-analyst`，家长端，尚未在任何账号实测）
