# WorkBuddy 从 GitHub 更新云端专家：能力核验

核验日期：2026-11-01。仅查看一手公开文档，未操作家庭账号或验证真实云端安装。以下将文档能力与部署推断分开；不能把 CodeBuddy CLI 的插件市场自动更新当成 WorkBuddy 云端能力。

## 已核实

- **已有专家可通过修改对话更新。** 在“我的专家”卡片菜单选择“修改专家”进入维护对话；官方说明该章节介绍客户端创建/管理。它证明有受支持的管理入口，不证明该维护对话对云端项目、资料和个人记忆完成自动迁移。[专家管理](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Expert-Center)
- **云项目有共享配置与资产。** 项目配置包含指令、专家、Skill、连接器，保存在云端；项目资料可上传或由任务产物保存，支持 RAG 和 read-file。Web与客户端个人Skill库不互通，项目级Skill云端统一管理。因此只写 ~/.workbuddy 或把ZIP解压到任务沙箱不能作为云安装成功证据。[项目配置、资产、双端差异](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)
- **个人授权有环境边界。** 官方称项目个人授权票据仅保存在成员本地、不上传云端，协作任务禁用个人授权连接器；公共授权由管理员配置。不能假定成人电脑的GitHub登录、PAT或连接器授权已经适用于孩子云任务。[项目授权](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)、[连接器](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Connector)
- **专家包是声明式能力定义。** plugin.json定义版本、Agent与Skill路径，可声明连接器或MCP依赖；所有工具权限由系统分配。文件中的“请安装”并不授予安装API权限。[专家开发规范](https://open.workbuddy.cn/docs/expert)
- **存在官方Open API，但公开列表没有直接专家安装/升级接口。** 当前列表覆盖OAuth2.1、个人资料、本地助理、云任务、ACP通信和会话产物等。接口需注册第三方应用及相应用户授权。实际HTML中的接口路径包括 /openapi/v2/tasks 和 /openapi/v2/localassistant；未发现直接专家CRUD、指定专家版本安装或云项目Skill发布端点。这是“未在所读公开接口中发现”，不能证明内部或未来绝无能力。[Open API](https://open.workbuddy.cn/docs/openapi)

## 对项目的建议（工程推断）

可以做“家长在两个账号分别触发一次的更新维护任务”：读取固定提交的发布包 → 校验包名/版本/SHA → 更新当前账号已有专家 → 关联云项目Skill和资料 → 在新云任务核验。若某步需界面授权/人工确认，流程准确停在该步，不能生成假成功回执。

本轮没有足够官方依据承诺“GitHub push 后两个孩子云专家无人值守自动更新”。即使用云任务API发送维护指令，仍需证明该任务具有真实云专家管理能力、能更新指定对象并返回可读回的版本；创建任务成功只代表任务已创建。

建议每个发布包提供release-manifest、适用账号槽位、目标专家标识、版本、源码commit与资产SHA，以及结构化安装结果。安装结果分 github_readable、artifact_verified、expert_updated、cloud_skills_visible、library_linked、new_task_verified；未知保持未验证，不能合并成“部署成功”。规则和共享资料可以升级，真实伙伴档案、阅读状态、账号凭据不随发布包覆盖或写回GitHub。分支仅用于分发，不是访问控制。

## 尚待两个真实云账号核验

1. 各账号的当前云入口是否能经已授权路径读取私有仓库固定提交；否则使用家长上传的ZIP，不在孩子聊天中传凭据。
2. 修改对话是否真正更新当前账号目标专家，而不是只改本机缓存或生成产物。
3. 六个项目级Skill和资料是否在新云任务中可选、可读取；家中电脑关闭后再测。
4. 是否存在已授权的真实版本读回、回滚和持久档案保护机制。平台没有公开事务式升级合同，不能仅靠提示词承诺原子回滚。

## 排除的混用

CodeBuddy Code文档有GitHub插件市场及第三方市场自动更新设置，但它属于CLI产品。WorkBuddy的Git/Worktree文档还明确当前Worktree Task不支持云端WorkBuddy；这些能力均不能当云专家自动部署证据。[CLI插件市场](https://www.codebuddy.cn/docs/cli/plugin-marketplaces)、[CLI自动市场更新](https://www.codebuddy.cn/docs/cli/release-notes/v2.97.0)、[WorkBuddy Git能力](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Worktree-Task)

访问说明：open.workbuddy.cn/docs/openapi 的web工具曾超时，已通过官方站点直接HTTPS读取并核对页面接口路径；未访问账号或第三方应用配置，不保存任何令牌或真实用户信息。
