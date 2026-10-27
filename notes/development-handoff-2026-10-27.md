# 学习伙伴v3 · 当前开发交接

2026-10-27。家长最新指示：“方案设计好了，你就开始开发，只要有额度你就不要停”。**已授权开发、必要测试和GitHub同步，不再等待确认。** 当前交付等级 ADULT_VALIDATION_ONLY；不能标儿童已可用。

> **最新增量：原生专家已成为当前用户试用入口。** 见 experts/learning-partner-momo 的 v1.1.6 与 experts/learning-report-analyst 的 v1.1.1 及各自 HANDOFF.md；保留用户最新平等、有趣、长期伙伴定位。原生记忆采用家长选择的长期陪伴设置，支持真实范围内拒记/改错/忘记；本 v3 自管工具仍为显式同意的可选路径。不要拿以下较早的 G04“必须关闭原生记忆”作为当前原生专家的要求。配套报告校验已增补至53项，成人运行时最新本机构建为 r4；下文48项/ r3 为前一轮证据。

## 1. 接续顺序

1. 看最新用户消息、git status、分支与远端，不覆盖其他AI改动。
2. 看本交接、workbuddy/final/CAPABILITIES.md、validation/v3/software-results.md。
3. 规则以final-plan-2026-10-27.md与engineering-plan-2026-10-27.md为基线，不重新拼旧方案。细节沿用家庭已确认决定。
4. 继续平台门槛与真实模型评测，不再重做113份课程调研或独立赛马。

## 2. 已实现和实际验证

- workbuddy/final：常驻伙伴规则、六个Skill、父母指令、真实工具合同、安装/维护/能力/变更说明。孩子包5个Skill，父母包仅parent-review。独立规格审查和质量审查通过，minor重复回执措辞已改为should_ask=false不问。
- companion：Python3.11+标准库核心、SQLite事务固定身份、幂等操作、版本冲突、同题辅助证据、阅读与愿望单、自选记忆、一次跟进、软提醒去重、90天事件/偏好清理、原子纠错与任务范围忘记、最小父母导出/Markdown、最新撤回和完成清单恢复、显式旧库迁移。
- MCP：官方SDK1.26.0固定版本，8个stdio工具，无模型可选路径/身份、shell、父母导出或恢复。真实子进程协议调用通过；没有冒充正式模型API。
- materials：147个原书目ID的去个人化发现候选，全部限制为目录识别，未迁入旧unread/owner/兴趣推测；3张本项目短方法卡。原文/照片/旧刘擎卡不直接发布给孩子。
- 本机macOS26.6.2、Python3.13.7、SQLite3.50.4；48项测试通过，含实际stdio与解压源码包跨进程CLI。依赖警告通过固定pydantic2.12.5/settings2.12.0解决。
- 分角色zip与SHA清单可复现；dist/v0.1.0-adult-test-a-r3、test-b-r3为本地最新构建。源码不依赖这些二进制才能接续。

核心独立审查发现的事件原位改写、完成/忘记任务复活、上下文非快照、裸类型错误、报告按ID选末次、旧物理库不迁移等已补回归修复。通过快照在GitHub提交51dff4a517b58a457a8e77859a49075b3e8cf51e（同树73adbfc6cd4f9c71ea4e3ca293475958b3e31965）。末批愿望单/清理/打包与部署在本地34125ef已独立复核通过；CI随后发现未跟踪合同文件和Windows编码/测试连接未关闭，已补修，第二轮三系统CI（run40423247956）全部通过，固定00c1a8b的补充独立复核也已通过。以software-results最新记录为准。

## 3. 仍未完成（不能写成通过）

G01国内实际账号/监护安排；G02两台实机图片/语音和纠错；G03真正加载规则与Skill；G04自动记忆关闭/已有记忆/历史召回；G05/G06实际OS和平台权限、手机与模式切换；G07–G10真实WorkBuddy续接、写入/失败、更正、导出恢复和父母空间。工具层通过不替代平台/OS。

42组真实模型/平台场景在validation/v3/scenarios.json，均保持not_run。没有真实孩子使用或教育效果证据。没有口语评分、整页批改、自动购买/消息/报警、网页并行开发。

本机WorkBuddy5.8.3，成人工作账号完全访问；未改它的记忆/全局权限/工作连接器。已创建learning-companion-adult-validation-v3测试空间。创建专家入口会转expert-manager任务草稿，不是静态表单；草稿已清空未发送，未创建或发布专家，未发模型验证。后续先核对当前任务实际所选空间，入口不一定继承。账号URL、签名、工作历史不入记录。

## 4. 下一步按此执行

1. 软件独立复核与三系统CI已通过（GitHub源4b8f406dc4f028440f170e8346168c9f850451e8）；无需对未改软件反复扩大测试。下一步集中真实WorkBuddy门槛。
2. 在专用成人/测试账号验证项目加载方式与输入。家长已确认两个学习专用账号准备好；已请家长把本机Mac切换到其中一个，家长随后回复“暂时不方便切换，先继续代码验证”；当前不再等待切换，也不操作账号界面。不索要手机号/密码/验证码。接受协议/注册监护实际步骤由家长完成，不能代替资格判断。
3. G01–G06关键门槛通过后，再跑真实端到端和T01–T42。W-A必须先实演人工快照/续接/导出/改删负担，W-B必须真实限制工具，不能打开完全访问补缺口。
4. 若实际无法持续约束可到达入口或家庭不能承担人工维护，依据批准方案转网页规格；不是因为额度或日期到了就提前扩路线。
5. 每个闭环更新状态/证据/交接并同步GitHub；只记录已做事实。当前开发分支codex/learning-companion-v3，默认main仍是之前方案基线；接续须先选择此开发分支或草稿PR #1：https://github.com/18523102883hao-boop/learning-assistant/pull/1。尚未合并。

可用干净目录直接取得当前源码：

```bash
git clone --branch codex/learning-companion-v3 https://github.com/18523102883hao-boop/learning-assistant.git
```

已有仓库先读git status并fetch后核对，不能覆盖其他AI工作。平台验证此刻需家长后续配合，但软件交接已完成。

## 5. 复现和数据边界

源码根执行：python3 -m venv .venv；安装requirements-mcp.lock.txt；pip install --no-deps -e .；python -m unittest discover -s tests -v。用安装的虚拟环境Python。bundle模块命令和Mac/Windows维护命令见workbuddy/final/RUNTIME.md。没有SDK时跳过MCP不算通过。

JSON合同v3、SQLite物理v4。真实数据在每人独立OS目录且在Git/源码外；父母目录不可挂给孩子。账号分开不等于OS隔离；窄工具不等于沙箱。普通聊不自动存，明确意愿才存可选记忆，自报不变掌握；父母报告不读原始聊天。

删除仅对自管内容有保证，平台自动记忆、历史、媒体、人工副本和旧备份分开。旧备份须当前撤回/完成清单；哈希不证明最新。报告更正新ID带supersedes，不能远删人工副本。资料三轴和版权/真实身份边界继续沿用材料审阅。

## 6. GitHub与本机

仓库18523102883hao-boop/learning-assistant。HTTPS git push曾低速超时；GitHub连接器可用，按本地提交内容建立tree核对SHA，再用expected_sha保护分支推进，不强推。API提交和本地提交SHA可能不同，但内容树必须相同；合适时读取远端commit对象核验再对齐本地引用，不覆盖工作文件或未提交更改。

本机课程原文仍在Obsidian Vault knowledge/parenting-agent-kb/transcripts_raw，刘擎原文在主工作区忽略的library/parent-materials；新worktree不含忽略全文。需要原句先确认文件，不从摘要编造。Git中已有113份通读/哈希与材料审阅可接续。
