# WorkBuddy 云端能力核验 · 2026-10-27

仅据当日官方文档核验，未操作账号或验证家庭云端任务；产品配置支持不等于每个入口已跑通。

## 已证实

1. **云上与本机是不同执行环境**：云上使用云端沙箱，无需个人电脑；本机模式远控桌面端。因此不能把家中 Mac 的路径、SQLite 或 stdio 进程作为云上必需依赖。[小程序概述](https://www.codebuddy.cn/docs/workbuddymini/quick-start/Overview)
2. **个人 Skill 库不自动互通**：官方明确 Web 与客户端个人 Skill 库互不相通；云上任务选不到客户端个人库 Skill。项目级 Skill 在云端统一管理，双端一致；项目配置包含指令、专家、Skill、连接器，保存在云端。故 GitHub 更新/本机目录更新都不等于云端专家已更新。[项目文档“Web端与客户端差异”](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)
3. **云端资料有官方承载**：项目资产支持上传文档，能通过 RAG 注入或 read-file 读取；任务创建注入项目指令、资料引用和个人记忆。资料库还支持个人“我的文档”，任务可引用读取/修改，MD 修改可能须审阅确认。文档未保证每次自动读到全部材料，上传后仍须检索实测。[项目](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)、[资料库](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Library)
4. **原生记忆定期整理**：默认开启，从历史提取事实、偏好、人物关系及待跟进；每晚整理，设置中可查看/编辑/删除、导入其他AI记忆并关闭；存在概括偏差与过时风险，不保证逐轮即写、全量召回。关闭/删记忆不会撤回已生成输出。5.9.1 更新明确优化云端记忆。[记忆](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Memory)、[更新日志](https://www.codebuddy.cn/docs/workbuddy/Changelog)
5. **远程 MCP 配置存在**：专家依赖可指向 .mcp.json；官方支持 url 指向远程 SSE/Streamable HTTP、type=http、headers 鉴权。另一方面，项目文档指出个人授权连接器票据仅本地、协作任务禁个人授权；不可假定本机授权已同步云端。[专家开发规范](https://open.workbuddy.cn/docs/expert)、[项目](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)

## 合理推断与仍待验证

可采用每个孩子独立云项目：共享不含个人信息的只读方法/书目，各自保留云端个人记忆与可更正的续接资料。临时沙箱文件不能当可靠数据库，GitHub只发规则资料，不发真实记忆。需要即时、可审计持久化时，远程鉴权服务是候选；须先实测云入口能发现/调用、票据可用与账号隔离。服务应按凭据固定孩子范围，不能让模型输入 child_id 决定访问谁。

未证实：本机“我的专家”自动出现在云入口、任意 references 文件自动随专家加载、云沙箱跨任务/重建持久性、每轮自动记忆成功、同账号跨环境完全等价、云端可直接调用本机 stdio。

## 两账号最小成人云验收

家中电脑关闭后，分别在云上专用账号：①确认专家版本和项目指令中的非敏感版本标记；②读取一个随包方法卡与书目ID，给出文件标题/条目，不凭模型自述“已加载”；③将“虚构纸船叫蓝星号”等最小合成事实保存至各自云端资料，读取回执与版本，新任务再读；④待原生记忆实际整理后，在新任务核对，再按设置更正/删除并复验；⑤另一账号应无法看到该合成事实；⑥若接远程MCP，另测保存、重试、更正、忘记及越权拒绝。每项记录真实工具/文件证据，未知即未通过，不上传账号信息或会话签名URL。
