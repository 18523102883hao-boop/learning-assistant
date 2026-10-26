# 两个孩子的引导式学习助手：平台核验

查询日期：2026-10-26（Asia/Shanghai）。范围：腾讯 WorkBuddy、腾讯云智能体开发平台 ADP、Dify。只做一手资料调研，未安装软件、未修改应用设置、未做账号内实测。腾讯元器与 ADP 是不同产品；下文 ADP 的隔离保证不能套用到元器。

## 结论与建议（研究判断）

建议先用 WorkBuddy 做三年级和五年级两个孩子的教学交互原型，验证“有帮助但不直接交作业答案”的对话是否让她们愿意持续使用。家庭两人试用，暂时不必为完整小程序和后台承担开发维护工作。WorkBuddy 已有移动端、小程序、图片和语音入口，不能依据早期印象把它当成只有桌面端的工具。本轮只确定路线，不部署。

但是，两个工作目录不等于两个独立用户。工作区文件、项目配置、任务上下文、平台自动记忆、账号及工具权限是不同边界。先保持两个孩子各自的显式学习档案；在自动记忆的范围未经实测前，建议在专门用于孩子学习的配置环境中关闭这项自动记忆，避免把同一成人账号的全局画像作为孩子学情。若要更强的独立使用边界，应使用符合平台条款的独立账号/设备或操作系统用户，或转向有应用级身份校验的专用前端。关闭自动记忆也不能单独证明文件与权限已经隔离。

如果试用后确认需要固定的儿童界面、身份锁定、限制工具、可靠的家长视图，再评估 ADP 或 Dify。两者都有明确的终端用户概念；仍需应用负责身份认证、学习证据存储和家长权限，而不是让模型通过聊天内容猜“现在是谁”。

## WorkBuddy：已核实事实

| 能力 | 官方事实与含义 | 一手来源 |
| --- | --- | --- |
| 工作区 Working Memory | 4.6.2 更新日志写明 Working Memory 按 workspace 独立存储。可作为局部记忆分离依据，不能扩展为全部记忆、账号与文件权限的隔离保证。 | [更新日志](https://www.workbuddy.cn/docs/workbuddy/Changelog) |
| 平台自动记忆 | 默认开启，从会话历史抽取个人信息并定期更新，每晚整理，可查看、编辑、删除、关闭。该页未说明以工作区为隔离单位。 | [记忆](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Memory) |
| 项目指令与配置 | 项目可配置指令、连接器、专家、Skills；新建任务自动继承。代码开发场景支持 `.codebuddy/rules/`、`agents/`、`skills/`、`commands/`、`CODEBUDDY.md`，兼容 `AGENTS.md`。项目配置优先于用户级同名配置，项目之间配置独立。 | [项目](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project) |
| 全局配置仍会加载 | WorkBuddy 官方设置页明确说，代码开发时会加载个人环境的用户级 `.codebuddy` 规则、Skills、Commands、MCP 并与项目配置合并。不要往全局规则或技能正文里写某一个孩子的个人画像。 | [系统设置](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Setting) |
| 全局与项目目录 | WorkBuddy 官方链接到 CodeBuddy 目录说明：`~/.codebuddy/` 属用户级，项目根的 `.codebuddy/` 属项目级。全局 `CODEBUDDY.md`、rules、skills 作用于各项目。这是官方明确说明的兼容关系，不能把其他 CodeBuddy 行为未经验证全部搬给 WorkBuddy。 | [官方所链接的目录说明](https://www.workbuddy.cn/docs/cli/codebuddy-dir) |
| 创建技能 | 支持从本地技能包导入，也可通过任务描述创建技能。Skill 启停状态保存在用户全局配置并可多端同步。Skill 可以调用第三方、执行命令或读写文件。 | [技能](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market) |
| 创建专家 | 官方入口是“我的专家 → 创建专家”；专家包包含 Agent 定义，可配套技能/连接器。专家适合承载稳定的角色与教学方法，技能适合可复用的局部流程。后一用途分工属于本研究设计建议。 | [专家开发文档](https://open.workbuddy.cn/docs/expert) |
| 手机入口 | 微信小程序支持文字、语音、图片和文件；云上模式使用云沙箱，不依赖个人电脑；本机模式遥控桌面端，并要求两端登录微信账号一致。 | [小程序概述](https://www.codebuddy.cn/docs/workbuddymini/quick-start/Overview) |
| 权限范围 | 默认权限以工作空间为主要边界，越界/高风险操作请求确认；“完全访问”是当前客户端内全部任务的全局开关；工具管控同样对客户端所有 Agent 生效。文件安全支持按路径配置读/写/删除的允许、询问或拒绝。 | [默认权限与安全沙箱](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Permission-Modes) |
| 本地与云端处理 | 官方支持内置和自定义模型；接入自定义第三方模型时输入会发往该模型。数据文件放在本地不能推出“孩子的内容只在本地处理”。 | [模型配置](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Model) |
| Open API | 已公开 OAuth 2.1、本地助理消息、云任务创建/查询、ACP 实时通信、会话产物等接口。因此“WorkBuddy 没有 API”不成立。公开创建云任务参数列出 `prompt` 和 `name`，不能据此断言存在独立 `child_id` 记忆域。 | [Open API](https://open.workbuddy.cn/docs/openapi) |
| 开放平台门槛 | 开放平台有技能、专家、连接器、Buddy 应用和外部接入；注册、资质认证及审核属于发布流程。第三方应用文档将完整业务 Scope 主要放在硬件接入类别，家庭自建 H5 的具体准入尚未验证。 | [概述](https://open.workbuddy.cn/docs)、[第三方应用](https://open.workbuddy.cn/docs/third-party-app) |
| 定制 WorkBuddy 入口 | Buddy 应用可配置工作模式、系统指令、首页场景及可用能力，也能集成已有系统；创建与发布需审核。存在该能力，不代表家庭账号现已能直接启用，或能锁住孩子所有切换入口。 | [Buddy 应用](https://open.workbuddy.cn/docs/buddy-app) |

### 用 Skills 还是别的方式？（设计建议）

组合比只写一个大 Skill 更合适：

- **固定教学规则/专家**：先识别孩子已有思路，每轮给一个短提示，允许孩子请求更明显的帮助；无证据不下人格或学习态度结论。
- **少量 Skills**：作业卡点辅导、真实任务探究、学习证据记录、家长周报。技能里放通用方法，个人进度放各自档案。
- **两个明确的孩子入口与存储目录**：共享课程材料与教学规则；每个孩子有固定 `child_id`，独立 `profile`、学习事件、掌握证据、复习计划。档案必须落在跨新任务可持续加载的位置；新聊天只是新会话，不能把“建两个聊天”当成身份与记忆方案。每次新建任务都要验证它仍指向正确孩子的档案，不依赖孩子在对话里声明姓名。
- **家长单独汇总**：报告读取经过确认的学习事件，保留日期、题型、提示层级、孩子解释与迁移验证。无需把全部亲子课程、全部聊天每天重复装入上下文。

这些是可实现的应用设计，不是 WorkBuddy 自带的学情诊断或儿童模式。提示词不能保证永远不给答案；必须用真实题目和“直接告诉我答案”等测试验证。

## 小型比较

| 平台 | 最适合当前需求的已核实能力 | 关键边界 | 家庭项目判断 |
| --- | --- | --- | --- |
| WorkBuddy | 项目/专家/Skills、本地文件、现成手机图片和语音入口；已有开放 API | 局部工作区记忆与自动个人记忆不能混为一谈；通用工具权限和客户端全局设置需处理 | 优先做受家长配置的教学原型；先验证实际使用体验 |
| 腾讯云 ADP | 长期记忆按“终端用户 + 应用”唯一；通过 `visitor_biz_id` 识别终端用户；提供 API 和多渠道接入 | `session_id` 与终端用户 ID 分别管理会话/用户；自动 `SYS.Memory` 在 Agent/工作流中只读，不能当可自由纠正的学情数据库；需核实所购版本功能 | 需要受控儿童界面、腾讯生态集成时的后续候选 |
| Dify | Chatflow 工作流、API、按 `user` 区分会话/文件，可自行部署 | Dify 不认证传入的 `user`；API Key 和用户身份映射必须留在可信服务端。会话变量只在一个 chat session 内持久化 | 更适合愿意维护应用/部署、希望把教学状态与数据库做清楚的后续路线 |

ADP 证据：[长期记忆](https://cloud.tencent.com/document/product/1759/122458)、[变量的用户/会话隔离](https://cloud.tencent.com/document/product/1759/122457)、[HTTP SSE 对话接口](https://cloud.tencent.com/document/product/1759/105560)、[官方产品页与渠道说明](https://adp.cloud.tencent.com/)。ADP 调试窗口已支持图片问答和可配置的语音交互，但具体渠道体验要另行测试：[对话调试窗口](https://cloud.tencent.com/document/product/1759/122607)。

Dify 证据：[终端用户身份](https://docs.dify.ai/en/api-reference/guides/end-user-identity)、[Conversation Variables](https://docs.dify.ai/en/cloud/use-dify/nodes/variable-assigner)、[自行部署](https://docs.dify.ai/en/self-host/deploy/quick-start/docker-compose)。Dify API 与它自己的托管 Web App 身份空间彼此独立，不能假定二者聊天记录自动互通。

**价格/权益边界**：ADP 官方产品页在本次查询时将长期对话记忆列于企业标准版能力。不能据此假定家庭试用/低阶套餐包含该能力。路线比较不需要现在购买；若选 ADP，先在实际控制台确认可用版本及费用。即使有自动长期记忆，两个孩子的结构化学习证据仍建议自存。

## 儿童条款与未确认项

WorkBuddy 开放平台开发者公约明确包含未成年人适配，以及面向不满 14 周岁用户取得监护人同意和额外保护的要求：[开发者公约](https://open.workbuddy.cn/docs/developer-agreement)。这是开发者资产的要求，并不替代消费端注册和使用条款。

大陆 WorkBuddy 文档链接的隐私原文位于[腾讯隐私保护平台](https://privacy.qq.com/document/preview/771d9a58551449e9a7e7445ebfe04966)，本次网页抓取未能获得正文。搜索找到的英文 `workbuddy.cn/document/term` 实际指向国际服务及国际签约实体，不能拿其中年龄要求替代中国版条款；第三方政策镜像也未作为确定依据。儿童正式直接使用前，应以届时国内客户端/小程序实际展示的用户协议和儿童隐私条款核实。

仍未知、不能承诺：

1. 同一 WorkBuddy 账号的自动个人记忆是否会跨项目注入。官方记忆页说明关闭或删除后相关数据停止用于后续对话；实际客户端仍需验证这一行为，并检查会话历史检索等其他信息路径。
2. 桌面、本机小程序、云上小程序能否加载完全一致的项目规则/私有 Skills/本地档案。
3. 能否以家长控制的方式限制孩子切换项目、开启完全访问、安装额外技能或读取家长报告。
4. 家庭自建前端可申请的 WorkBuddy 开放平台应用类型、审批范围及实际费用。
5. 当前套餐下 ADP 长期记忆的可用性，以及两个孩子手写题、中文朗读、英语口语的实际识别质量。

## 原型验收建议（尚未执行）

- 孩子 A 写入无敏感性的独有测试事实，切换孩子 B、新建会话、重启后确认不会出现 A 的事实；分别测同目录/不同目录、自动记忆开关、手机云端/本机。
- 每个孩子再新建任务，确认自己的 `child_id`、学习档案和已确认掌握证据仍被正确加载，既没有串档也没有因临时工作区切换丢失长期记录。
- 在 B 的会话中明确要求读 A 的目录和家长周报，验证权限层拒绝，而不仅是模型口头说不会读。
- 用同一道题测试直接要答案、连续请求更明显提示、上传模糊图片、只说“不会”、中途返回；核对是否短而有帮助，并提供孩子能自己完成的一小步。
- 将同知识点的另一道题放到隔天验证，区分“刚才跟着做对”和“能够独立迁移”。
- 报告只写观察事实与待验证假设，例如“本周 3 次需要画图提示”；不把短回复、求答案、停顿自动解释为不认真或懒惰。

## 方法记录

先查 Context7 官方文档索引，再打开所属产品的官方网页。命中的库为 `/websites/codebuddy_cn_workbuddy`、`/websites/cloud_tencent_document_product_1759`、`/langgenius/dify-docs`。WorkBuddy 与 CodeBuddy 的兼容仅采用 WorkBuddy 页面主动声明或链接的部分；不将社区帖、第三方教程或另一个同名产品当官方依据。
