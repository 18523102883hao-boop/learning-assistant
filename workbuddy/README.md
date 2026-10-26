# WorkBuddy 原型部署说明

目标：在 WorkBuddy 上搭建两个孩子的引导式学习助手原型，先验证教学体验，暂不开发定制前端。

## 版本目录（赛马机制，2026-10-26 家长决定）

| 目录 | 版本 | 说明 |
| --- | --- | --- |
| `kimi/` | **Kimi 版 v1.0**（当前完整版） | 按 `notes/master-proposal-2026-10-26.md` v1.0 编写：四个入口（含伙伴模式 partner-chat）、第 0 级情绪接收、语言 lint、冷启动剧本、注意力护栏、周报落文档 |
| `codex/` | **Codex 版**（待 Codex 编写） | 结构同 `kimi/`（PROJECT_INSTRUCTIONS.md + skills/），由 Codex 按自己的想法从零写，不得先读 kimi 版再"参考改写"——赛马要比原始判断 |
| `final/` | **最终版**（待 Codex 综合产出） | Codex 对比两版后提取优点合成；合成时须逐条注明取舍来自哪一版及理由，写入 `final/CHANGELOG.md` |

**赛马规则**：两版同时可用 WorkBuddy 实测（各绑一个孩子的项目跑 A/B），或以家长评审 + Codex 综合定稿。部署时只需把对应版本目录的内容粘贴/导入 WorkBuddy。

## kimi/ 版构成

| 组件 | 文件 | 作用 |
| --- | --- | --- |
| 项目常驻指令 | `kimi/PROJECT_INSTRUCTIONS.md` | 身份（平等伙伴）+ 教学约定 + 语言 lint + 冷启动剧本 + 注意力护栏 |
| Skill：作业卡点 | `kimi/skills/homework-help/SKILL.md` | "帮我过这一关"：第 0 级情绪接收 + 四级帮助 + 跳级 + 迁移验证 |
| Skill：探索创作 | `kimi/skills/explore-task/SKILL.md` | "我想弄明白"流程 |
| Skill：伙伴闲聊 | `kimi/skills/partner-chat/SKILL.md` | "随便聊聊"：平等伙伴对话 + 五条红线 + 收口护栏 |
| Skill：学习记录 | `kimi/skills/learning-log/SKILL.md` | 学习事件写入（含 scene_type 场景分类） |
| Skill：家长周报 | `kimi/skills/parent-review/SKILL.md` | 仅家长入口；含场景分布行与周报落文档 |
| 孩子档案 | `../profiles/*.example.json` | 固定 `child_id`，独立保存 |
| 事件格式 | `../schemas/learning-event.schema.json` | jsonl，一条一行 |

## 部署步骤（待执行）

1. 在 WorkBuddy 建一个「孩子学习」项目，把选定版本的 `PROJECT_INSTRUCTIONS.md` 内容粘贴为项目指令。
2. 通过「从本地技能包导入」逐个导入该版本的 Skill，确认项目内启用状态。
3. 把两个示例档案放到项目内固定目录（如 `profiles/`）；新建任务时显式读取当前孩子的档案。
4. **关闭未验证的自动记忆**（官方记忆页可关闭），以显式档案管理个人信息；关闭不等于隔离，仍需做验收清单中的串读测试。
5. 用**虚构**测试档案做隔离验证（见 `../validation/prototype-checklist.md`），通过后再换真实（去标识）档案。

## 必须记住的边界（来自平台调研）

- 两个工作目录 ≠ 两个独立用户。工作区文件、项目配置、任务上下文、自动记忆、账号权限是不同边界，逐项验证。
- 不要往全局（用户级）规则或 Skill 正文里写某一个孩子的个人画像；全局配置会与项目配置合并加载。
- 全局「完全访问」开关、工具管控是客户端级的，孩子使用前需处理。
- 桌面端 / 本机小程序 / 云上小程序能否加载一致的项目规则与档案，需要逐端实测。
- 作业照片优先裁掉姓名、学校信息；本地保存文件不代表推理过程全部本地化。

## 何时换路线（来自设计稿 §7）

试用后若确认需要固定儿童界面、身份锁定、限制工具、可靠家长视图，再评估腾讯云 ADP（长期记忆按终端用户+应用隔离）或 Dify（自行部署，`user` 字段隔离但需自证身份）。
