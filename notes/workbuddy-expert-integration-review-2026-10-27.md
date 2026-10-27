# WorkBuddy 原生专家集成审查 · 2026-10-27

本次以用户给出的两个本机专家目录和 GitHub 专家分支为对象，保留最新本机自定义与陪伴定位。目标是将已确定的教育原则放入 WorkBuddy 真正加载的原生结构，而不是让用户另搭一套聊天入口。

## 原生结构与加载职责

- `.codebuddy-plugin/plugin.json`：专家名称、版本、agent 路径、随包 Skill 路径与展示信息；homepage 为 URL 字符串，默认提示语与首快捷语一致。
- `agents/*.md`：英文描述和双语展示 frontmatter，正文为常驻行为，skills 列表预加载方法。
- `skills/*/SKILL.md`：意图方法，references 为随包只读资料，scripts 为在系统实际分配权限时可执行的真实程序。
- 本地 marketplace 的 source 指向源码目录，已安装插件另有版本化 cache 与 installed_plugins.json。源码修改不等于旧会话已经加载；安装记录、实际缓存内容和新会话需分别核对。
- 官方不允许开发者在专家定义中任意添加 tools；本包不添加虚构工具或擅自开启权限。MCP 依赖仅在真正有相应服务、身份与路径时再配置。

官方依据：https://open.workbuddy.cn/docs/expert ；https://open.workbuddy.cn/docs/skill ；原生记忆：https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Memory 。

## 保留与修复

- 保留用户最新“有趣、平等、长期伙伴”的定位、小档案和头像；教材只作为爸爸提供的线索，学校版本、册次与进度待核。作业时不主动发散，闲聊与探索仍可有趣。
- 家长已明确选择“重要要点默认保留”的长期陪伴方向。使用真实 WorkBuddy 原生记忆：平台定期整理，不能承诺每轮立即写入、立即跨会话可读，或一句“别记”已阻止全部提取。拒记、更正和忘记先停止引用，再根据实际设置/结果处理。
- 原生记忆与 v3 自管学习记录分开；不能把原生默认设置伪造为自管工具的 child_opt_in=true，不自动统计普通闲聊。
- 保留家长“成长手记”定位。它主要使用当前有效、可向家长分享的最小要点 shared-moments/1；不抓取原始私聊或全部记忆。随包只读 validate_input.py 对格式、分享标志、重复字段、期间和重复ID检查，不写报告、不访问网络。
- v3 parent-export 仅有受限学习证据，没有兴趣、书名或作品细节；手记不能从枚举补写生活。v3 兼容路径需要实际安装运行时，否则明确返回 runtime_unavailable。
- 移除虚构 journal/journal-status 命令；区分输出文本与真实保存。模板按输入类型分别使用 moment_id/source_id/revision 或 event_id/source_store_id/source_sequence。
- 修复 references 被根忽略规则漏提交的问题，按实际模板路径精确放行；运行缓存 pyc 不入库。旧未核书库和个人资料不再随新专家包发布，既有历史不擅自重写。

## 验证与局限

孩子包4项、家长包6项自动检查通过，覆盖路径/元数据、脱敏目录、可分享输入、错误输入、重复分享字段、UTF-8新进程和旧运行时防误报。它们是静态与程序验证，不能证明真实 WorkBuddy 模型行为。

v3 配套校验补上来源元数据类型、事件日期/序号范围、重复ID与来源/帮助/独立性约束；53项软件测试通过。旧记录缺有效核对时保守呈现为不能判断正误，旧报告格式须重生，不能因“correct”标签就声称已核对。

独立只读复核分为孩子行为、家长/数据与资料结构；发现项已逐项处理。外部 Codex CLI 独立复核因账号额度中断，没有把该项记录为通过。头像、技能路径和所有必需引用还要从干净 Git 归档验证，实际平台加载、媒体、权限和记忆保留/更正/删除仍由用户在 WorkBuddy 测试。

两个专家各带 TESTING.md。需重启或重新召唤专家并开新会话；旧会话可能持有旧提示词和技能。账号/OS隔离与原生记忆范围不由提示词保证。
