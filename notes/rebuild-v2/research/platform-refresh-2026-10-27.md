# WorkBuddy 与学习工具官方事实补核（2026-10-27）

用途：给最终讨论方案提供可交接的事实边界；不代表已选定、配置或验收平台。本次只查公开一手资料，未注册、安装、登录、部署或修改任何配置，没有使用真实儿童资料做测试。

核查日期统一为 **2026-10-27（Asia/Shanghai）**。工具时钟返回 `2026-10-26 16:26:41 UTC`，换算为北京时间为 10 月 27 日 00:26:41，并非日期冲突。页面未提供更新时间时，以下只标本次查阅日期；搜索引擎抓取时间不当作功能上线日期。可见桌面更新日志最新条目为 **5.9.2，2026-10-26**；其中 4.6.2 等条目仅是历史发布记录，不证明家庭设备已安装相同版本。

先读了本仓库的 `research/product-and-platform-facts.md`、`TECH-ROUTE.md` 及 `notes/workbuddy-platform-research-2026-10-26.md`，随后重新打开官方页面查证。旧文不是本次结论的证据。下列每个链接的查阅日期均为上述日期。

## 1. 输入：有功能说明，不等于这两台电脑已经可用

| 入口 | 官方资料直接支持什么 | 尚不支持的结论 |
| --- | --- | --- |
| Mac 桌面端 | [任务对话](https://www.workbuddy.cn/docs/workbuddy/Conversation)写明图片上传、拖拽、`Ctrl/Cmd + V` 粘贴；[更新日志](https://www.workbuddy.cn/docs/workbuddy/Changelog)5.9.2 写明语音识别终稿回填输入框及语音快捷键调整。属于桌面通用说明。 | 未逐台测试麦克风、快捷键、手写题识别与等待时间；未查到桌面原生调用摄像头拍纸题的明确操作说明。 |
| Windows 桌面端 | 同一套桌面文档支持图片入口，桌面更新日志已明确存在语音输入；文档没有在这些语音条目中单列 Windows 例外。 | 不能把通用说明写成 Windows 实机验收通过；两系统的硬件、安装版本、系统权限仍须分别验证。 |
| 手机 App | [发起任务](https://www.codebuddy.cn/docs/workbuddyapp/features/Create-Task)说明麦克风录音后转文字发起任务；[附件页](https://www.codebuddy.cn/docs/workbuddyapp/features/Attachments-and-Skills)说明实时拍照、相册选择、文件上传，照片可在发送前移除。 | 这是语音转文字入口，不是儿童朗读评测、口语评分或完整实时语音家教。图片输入也不是专门的拍题批改承诺。 |
| 微信小程序 | [官方概述](https://www.codebuddy.cn/docs/workbuddymini/quick-start/Overview)写明文字、语音、图片、文件，以及云上与本机两种执行环境；本机连接要求小程序与电脑微信账号一致。 | 不据此推定 App、小程序与桌面端的配置、记忆、权限和输入交互完全一致。 |

图片理解须选实际支持视觉输入的模型。[手机附件页](https://www.codebuddy.cn/docs/workbuddyapp/features/Attachments-and-Skills)有这一条件，但其举例与当前[桌面模型清单](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Model)不完全一致。方案应要求检查实际客户端的视觉能力标记并用同一张虚构题验证，不把某个旧模型名称写成永久兼容保证。

**设计含义（本研究判断）**：可以复用原生图片和语音入口做候选路线；仍须选定每个孩子实际使用的拍摄设备。不能从“已有 Mac 和 Windows”推出“两人都有低负担的拍题路径”。

## 2. 手机连接电脑、微信消息与 Ask 模式是不同概念

### App 连接电脑：有明确的工作空间续接路径

[多端协同](https://www.codebuddy.cn/docs/workbuddyapp/features/Multidevice)直接说明：Mac/Windows 桌面端开连接许可，两端同一账号且均联网；手机可进入已有工作空间/对话续聊，在当前任务里新建任务可沿用当前工作空间，并可发送手机照片及文件。电脑锁屏持续执行还依赖保持唤醒设置。

同页还明确：手机可选择电脑已安装的技能、专家、连接器及模型，并可从默认权限切到“允许完全访问”；连接器首次授权和模型新增配置仍在电脑完成。清单以电脑为准，断连时不可改。**手机因此也能触达电脑的操作能力，不能当作天然的儿童权限外壳。**

语音转文字与远程发送在两份官方说明中分别存在，因此“手机口述→文字指令→目标电脑任务”是有文档基础的组合候选；“拍同一题、补一句语音、始终进入正确孩子项目”尚未实测，不能宣称已跑通。同账号多部手机可同时收到这台电脑的任务通知，也不能忽略家长手机登录安排。[同页来源](https://www.codebuddy.cn/docs/workbuddyapp/features/Multidevice)

### 微信等 IM 助理：不能直接等同 App 选工作空间

[微信助理指南](https://www.codebuddy.cn/docs/workbuddy/WeixinBot-Guide)支持图片、文件及语音指令（依赖微信语音转文字）；执行使用电脑上的文件、Shell、凭证、插件和工具，原有安全策略仍适用。电脑休眠、断网或退出客户端会中断远程访问。

但[助理总说明](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Assistant)把助理描述为固定专属文件夹、单一持续会话，历史不可清空；解绑也会保留既有本地历史。这与普通任务自由指定目录不同。两个官方页面对“可访问原项目”与“实际执行目录”的介绍层次不同，尚不足以证明微信消息能稳定选中某个孩子的学习项目。应将该点留作现场验证，不能以接通机器人代替验收。

### Ask/Plan/Agent：工作模式，不是账号权限

[新建任务栏](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Task-Bar)定义三档：Agent 可执行与改文件；Plan 先给方案、确认后执行；Ask 仅问答，不做执行。它们与“默认权限/完全访问”是两个维度；用微信发一条普通消息也不意味着进入 Ask。

**设计含义（本研究判断）**：若用 Ask 作为先期讨论入口，就不能同时默认它会自动写学习档案；记录可以先由家长确认摘要，之后再验证受控写入。Ask 文档也没有给出不可由孩子切换的家长锁承诺。讨论方案须明确所说的“消息模式”究竟指 IM 远程通道还是 Ask，避免把两者合并。

## 3. 账号、项目、工作目录与记忆的边界

| 层次 | 官方承诺/描述 | 不可扩大解释的边界 |
| --- | --- | --- |
| 任务与工作目录 | [任务栏](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Task-Bar)说任务各有工作空间与上下文；[任务管理](https://www.codebuddy.cn/docs/workbuddy/Task-Management)说空间重命名仅改显示名，不改实际路径。 | 目录名称、两个聊天或两个项目都不是儿童身份认证，也不构成 OS 文件访问隔离。 |
| Working Memory | [更新日志](https://www.workbuddy.cn/docs/workbuddy/Changelog)4.6.2（2026-03-20）记载按 workspace 独立存储。 | 只支持这一类工作记忆的存储划分，不能推广为所有个人记忆、历史检索、共享配置及工具都隔离。 |
| 自动个人记忆 | [记忆说明](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Memory)说默认开启，从历史提取事实、偏好、人物关系、跟进事项；每晚整理、仅本人可见，用作系统上下文并支持历史检索。 | 官方没有把“本人”定义成同账号下由聊天自报姓名区分的不同孩子，也没有承诺按项目各有个人画像。 |
| 个人记忆进入项目 | 现行[项目说明“发起任务”](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)明确列出项目指令、项目资料库与个人记忆进入项目任务上下文。 | 旧稿“个人记忆是否进入其他项目完全未知”应更新：进入项目已有明文；具体相关性筛选、账号间实现及家庭配置效果仍未实测。 |

记忆页支持查看、编辑、删除、关闭；关闭后停止新提取，关闭/删除的相应数据停止用于后续对话，已有输出不追溯撤回。其自动抽取也可能有概括偏差。因此自动记忆不能直接当成准确、可审计的学情数据库。[记忆来源](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Memory)

**设计含义（本研究判断）**：两个合规独立账号是身份安排，独立目录是数据组织，操作系统用户/文件访问控制是另一层措施。双账号不会自动改写运行进程所能访问的本机文件。若继续 WorkBuddy 路线，须另测跨新任务续接、另一个孩子目录、家长资料与跨端配置，不能只测昵称；共享 Skill 正文不应承载某个孩子的画像。这里尚未设置任何隔离或关闭任何记忆。

## 4. 项目指令、Skills 及工具权限

### 配置加载与调用

| 官方来源 | 直接支持的结论 | 本方案应保留的限制 |
| --- | --- | --- |
| [项目](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project) | 项目指令由任务继承；项目 Skill 是可调用能力。代码开发时读取 `.codebuddy/`、兼容 `AGENTS.md`；同名配置项目级优先。Web 与客户端个人 Skill 库分开，项目 Skill 云端统一。 | `AGENTS.md` 与 `.codebuddy/` 的兼容有“代码开发时”的限定，不能直接保证日常办公/Ask/手机云任务全部同样加载。项目配置隔离不等于文件权限隔离。 |
| [系统设置](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Setting) | 代码开发加载用户级 `.codebuddy` 的规则、Skills、Commands、MCP，并与项目配置合并。 | 只建项目目录不能推出全局配置不再参与。 |
| [技能说明](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market) | 技能可以读写文件、执行命令、调用第三方；启停记录在用户全局配置并可多端同步。关闭后新任务不再调用，但当前会话已加载的技能仍可用，新会话才完全生效。 | Skill 是流程/能力封装，不是账号、持久学情库或权限沙箱；“已安装”不保证每轮必然触发，也不能用关闭开关证明旧会话已经卸去能力。 |
| [开放平台技能格式](https://open.workbuddy.cn/docs/skill) | `SKILL.md` 的 `description` 要说明用途和触发词；正文可引用参考文件，脚本可经 Bash 执行。 | 该页未承诺所有模式的具体自动匹配顺序、触发成功率或任意参考文件始终常驻。核心伙伴约定不宜只寄托于按需技能触发。 |

### 权限范围

[默认权限与安全沙箱](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Permission-Modes)说明：默认权限以工作空间为主要边界，越界或高风险操作可要求确认；“允许完全访问”对当前客户端所有既有及新任务生效，不跨设备。安全中心可按路径分别控制读/写/删、按命令及网络设规则；工具/MCP 禁用在实际调用前拦截，策略也是当前客户端所有 Agent 共用。

同页的“受限模式”是工作区信任机制：不自动加载/运行工作区开发配置、规则、脚本及依赖它们的能力，仍可浏览搜索编辑文件。不能把它描述成“教学 Skill 正常运行且完全锁住电脑”的儿童模式。macOS 的完全磁盘访问、辅助功能、自动化授权另属系统权限；文档没有证明 Mac 与 Windows 的所有操作能力相同。

**设计含义（本研究判断）**：分别讨论工作模式、项目提示、工具禁用、文件规则和系统权限；不能把提示词“请勿越权”当成实际拦截，也不能声称平台已有不可绕过的家长锁。默认权限和受限模式都应在具体教学与记录路径中验证，不能预先承诺“功能全保留且零确认”。

## 5. 未成年人使用资格：仍须现场核对国内条款

国内官方文档链接到的[服务协议](https://rule.tencent.com/rule/202603180001)本次两次抓取超时；[PC 端隐私指引](https://privacy.qq.com/document/preview/771d9a58551449e9a7e7445ebfe04966)首次仅返回需 JavaScript 的壳，重试仍未获得正文。因此 **未查证国内个人版针对三、五年级孩子的注册资格、监护授权流程与具体有效条款**；两个手机号可用不等于已证明能够按条款给两个孩子注册。

可读的[开放平台开发者公约](https://open.workbuddy.cn/docs/developer-agreement)明确面向未成年人的内容要适龄、避免诱导付费与非必要收集；AI 拟人互动须提示 AI 身份，面向不满 14 周岁用户须取得监护人同意并采取额外保护。它约束开放平台资产开发运营，**不替代国内消费端准入协议**。国际版/Enterprise 条款、第三方政策镜像均未用于补齐这一空白。

后续由成人在实际国内桌面/App/小程序核对各自展示的协议标题、版本/生效日、年龄资格、监护程序及数据控制入口，再决定直接使用安排。本轮仍可完成讨论方案，无须现在注册或让孩子登录。

## 6. 定时、导出、删除与费用

| 事项 | 官方直接支持 | 尚未证明/容易误写处 |
| --- | --- | --- |
| 定时 | [定时任务](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Automation-Guide)区分本地/项目/云端。本地依赖电脑与客户端；默认权限可能停在等待确认。云端可离线于电脑执行，但不能访问本机路径。任务沿用相应登录身份与授权。 | 不能承诺云端自动读取本机儿童档案，或“定时=无条件可靠交付”。项目定时仅创建者可见，不是已有跨账号家长周报系统。 |
| 产物导出 | [手机产物页](https://www.codebuddy.cn/docs/workbuddyapp/features/Share)说明可导出 PDF、DOCX、Markdown 或腾讯文档。 | 不等于全部对话、自动记忆、Skills、权限与配置均可一次完整导出。个人版整体导出/恢复范围本次未获得完整官方承诺。 |
| 任务/目录删除 | [任务管理](https://www.codebuddy.cn/docs/workbuddy/Task-Management)说删除任务会从所有设备移除且不可恢复；“从列表移除工作空间”不会删除本地文件夹。[数据管理](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Data)支持取消分享，链接随后不可访问。 | 归档、移除目录、取消分享与物理删除是不同动作；未证明删对话同步删除提取记忆、外发副本或备份。 |
| 定时删除 | [定时说明](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Automation-Guide)说删云端定时任务后，已产生的云端会话仍保留。 | 不能把停止触发等同抹除历史。 |
| 注销 | [账号注销](https://www.workbuddy.cn/docs/workbuddy/Account-Cancellation)说明有 15 天冷静期，完成后相关账号数据永久删除，关联 CodeBuddy 账号同步注销；自动续费等要先自行处理。 | 不将其扩大为能追回已分享、已下载或第三方服务中的副本。本轮不执行注销。 |
| 当前个人版价格 | [定价页](https://www.workbuddy.cn/docs/workbuddy/Pricing)列体验版免费，标准/高级/旗舰非连续月付为 99/199/999 元；连续包月为 70/140/700 元，包年另列；积分赠送和部分额度写有“限时”。同账号 WorkBuddy 与 CodeBuddy 共享积分。 | 是本次看到的标价，不是家庭账单、实测每题成本或对未来促销的承诺；未承诺两独立账号共享订阅。预算仍需实际权益和用量验证。 |

[模型配置](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Model)另说明自定义模型输入会直接转发第三方，费用由用户向第三方支付。不能从“文件在本地”推出儿童信息完全不出设备；项目配置也有云端保存和资料库进入上下文的机制。方案应写清具体所用模式和数据去向，不把会员、API 及自定义模型权益混算。

## 7. 五个学习工具：只借鉴可见交互机制

以下均为厂商自己的说明；没有在本次取得这些机制对本家庭三、五年级孩子有效的实测证据，更不是品牌排名。

| 工具与一手来源 | 官方公开的交互 | 本项目可借鉴的设计判断与证据边界 |
| --- | --- | --- |
| 讯飞：[学习机功能页](https://edu.iflytek.com/solution/family/learning-pad) | 测—学—练、知识点微课、启发式答疑与板书；脚注限定“规划学/追根溯源”在初中数学，部分错因分析/点拨在小学与初中数学。 | 找当前具体卡点，短讲解后看孩子行动。不能把总览的所有功能视为三、五年级全科可用，更不能用广告中的提分表述替代效果验证。 |
| 学而思：[好未来官方新闻](https://www.tal.com/zh-cn/news/detail/1850) | 本次正文页面返回空，官方域名的搜索摘录可读，介绍“随时问”图像输入题目、逐步对话讲解。 | 仅作为历史产品声明、有限证据：纸上做题→传当前问题→分步对话。不能确认 2026 所有型号覆盖、最新体验或教育效果；不把摘要冒充全文核查。 |
| Khanmigo：[2026 年动机设计说明](https://blog.khanacademy.org/student-motivation-hard-problem/) | 答题前提示与策略；学生尝试答错后，可以并排看错误、直接解释并给同技能练习。页面显示 2026-10-07/10-13 两个日期。 | 帮助量随实际尝试改变；不把启发式固化为无限反问。文章是产品团队设计及观察，不能直接外推为中文家庭陪学效能。 |
| DragonBox：[Algebra 5+ 官方页](https://dragonbox.com/products/algebra-5) | 操作即时反馈，图案卡片逐步换成变量、数字。 | 先操作/比较看到后果，再连接数学符号。网页说明不证明孩子已会课本迁移；本期 WorkBuddy 也未验证具备同样互动白板。 |
| Duolingo：[Explain My Answer](https://blog.duolingo.com/explain-my-answer-now-free/) | 用户按需点解释，反馈针对当前错误及语言规则，并提供正确/错误对照；页内列出语言覆盖范围。 | “小提示/教这一步/换讲法”由孩子选择。既不据此保证英语全部课程都有，也不把一段宣传解释当成长期学习成效研究。 |

共同设计判断：让当前问题容易进入，给能推动下一步的反馈，把有意义的动作留给孩子，并允许随时停止。这是从上述机制得到的本项目推演，不是厂商对本项目的共同保证。

## 8. 交给主方案的改写要点

1. 可以写“复用桌面图片/语音与手机拍照作为候选”，不能写“两台设备已验收”；电脑摄像头拍题尚无明确证明。
2. 先把 App 连接电脑、IM 助理、手机云端分开；前者有现有工作空间续聊路径，另外两者不能默认指向同一学习目录。
3. 用 Ask 减少执行时，记录方案须同步调整；不得同时无依据承诺自动落盘。
4. 自动个人记忆明确参与项目任务，Working Memory 按目录的历史说明不能替它作隔离保证；双账号也不是 OS 隔离。
5. 手机可改完全访问；工具管控和完全访问是客户端范围。提示、技能与项目名都不能充当家长锁。
6. 国内未成年人准入与监护流程仍待实际客户端核对；不能以开发者公约或国际版年龄条款代答。
7. 产物可导出、任务可删、云端定时可离线执行均有官方依据；完整可迁移性、全面清除与跨账号家长报告仍需单独设计和验证。
8. 当前标价可以说明计费结构；“每月够不够、每题多少钱、效果多好”仍没有本家庭实测。学习工具的交互启发与效果证据继续分开。

以上为讨论与后续验收输入，不启动实现，也不构成对平台绝对隔离、儿童适用性或学习效果的承诺。
