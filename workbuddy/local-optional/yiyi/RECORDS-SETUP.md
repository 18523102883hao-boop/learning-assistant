> 历史本机适配器归档，不是当前云版安装入口。需要本机使用时应从1.1.0归档完整复现，不直接将本目录叠加到云版。现有私有数据不删除。

# 一一学习记录 · 安装与验收

本包 v1.1.0 将原生陪伴记忆与自管学习证据分开。缺少 save_learning_record / consume_reading_followup 确实意味着第二层没接；不代表 WorkBuddy 没有原生记忆。v3 分支未合并并不妨碍安装一个经过验证的独立本机运行时，不需要先合并 main。

## 当前 Mac 安装布局

- 专家：~/.workbuddy/plugins/marketplaces/my-experts/plugins/learning-partner-yiyi；缓存由安装记录选定，不依赖源码目录恰好打开。
- 固定运行时：~/.workbuddy/learning-companion/runtime/0.1.0-r4，独立 .venv 与正式安装的 companion 包，启动使用 -I，忽略当前项目和 PYTHONPATH；不依赖开发 worktree。
- 私有绑定：~/.workbuddy/learning-companion/bindings/learning-partner-yiyi.json，模式600，不进 Git。
- 私有数据库：~/.workbuddy/learning-companion/data/student-b/state.sqlite3；目录700、数据库600，不进 Git。仅昵称和三年级，不保存全名或生日；初始化后无学习、阅读或聊天测试记录。

运行时来自代码提交 ab4f552aa3751df9f42ac637509a4e01c177dcba 对应 r4 runtime-source.zip，SHA256 为 8213b3ee6eba60856141af421e68066b669bb07ae96f4be4f9139e58d9b62f14。MCP1.26.0 与 requirements-mcp.lock.txt 的依赖已安装。固定 child_id=student-b 是本机部署代号，不是自然语言姓名，也不是物理身份认证。

## WorkBuddy 中最后的连接

1. 由家长确认当前是一一专用账号，在新会话召唤“伙伴 · 一一”v1.1.0。
2. 按依赖卡片连接“一一的学习记录”（learning-records-yiyi）。官方专家依赖可通过 plugin.json dependencies.mcpServers 指向 .mcp.json，实际权限与启用以客户端为准。
3. 在工具记录中确认实际发现八个工具；先用 companion_context(false) 验证不返回个人信息，确认本次说话者后读取 true，绑定只能为 student-b。没有这些实际证据，不标平台集成通过。
4. 按 TESTING.md 的第二层场景跑成人虚构测试。已有旧会话不会自动重载全部指令。若依赖未出现，先核对版本与缓存，再从连接器页面按本包 .mcp.json 配置。不要开启完全访问作为修复方式，也不让孩子复制命令。

本配置通过当前 Mac 的 python3 启动轻量 stdlib 启动器，再转入固定 venv。若 WorkBuddy 找不到 python3，成人在本机 .mcp.json 的 command 填这台电脑实际 Python 的绝对路径即可；args 的 CODEBUDDY_PLUGIN_ROOT 由平台展开。没有绑定时启动器失败关闭，不会初始化空库冒充成功。

## 新设备安装（交给成人或后续开发 AI）

1. 从 codex/learning-companion-v3 固定版本取得运行源码与锁文件；核对归档哈希后解压到新的运行时版本目录，不能覆盖既有版本。用 Python3.11+创建 .venv，安装锁文件，再 pip install --no-deps 该运行时源码（正式安装，不用依赖临时 worktree 的 editable 模式）。本机53项软件测试及虚构 stdio 验证通过再接真实入口。
2. 在 Git 仓库外初始化新的 student-b 私有根目录；已存在的库不得重建或覆盖。用该 .venv Python 执行 companion init 与 doctor。旧设备迁移必须走备份、当前撤回清单和恢复流程，不能复制旧库复活已删除事实。
3. 私有绑定严格只有 schema_version、child_id、runtime_root、python、data_root、materials 六字段；schema_version=1、child_id=student-b，其余是该机绝对路径。python 必须是上述运行时内部 venv，materials 指向该运行时 materials/catalog.v3.json，data_root 与运行时分开。文件模式600。本机绑定不随专家包发布。
4. Windows 需要在其 OS 用户下重做独立安装、目录ACL和绑定，将 .mcp.json 的 command 改成该机可运行的 Python绝对路径；不能复制 Mac 绑定。Windows WorkBuddy 平台加载与 ACL 尚未在家庭实机验证。

## 数据与能力边界

- 最小学习事件仅记录真实可见尝试、帮助、结果与来源；“我会了”不变成已独立掌握，同题多轮不记成多次失败。普通闲聊不自动变为学习事件。
- 原生记忆可以保持长期陪伴方向；平台定期提取与历史保留不受此 MCP 控制。自管可选兴趣/作品记忆继续须明确愿意；单本一次跟进须另有同意与实际消费回执。没有回执时说“这次学习记录尚未保存”，不笼统说“我什么都记不住”。
- 八工具不提供家长导出、备份恢复、shell、任意路径或其他孩子参数。家长报告另走成人维护流程，成长手记不会自动跨账号抓孩子私聊。
- 固定工具身份只能防止通过工具参数切换孩子，不能证明坐在电脑前的人是谁。相同 OS 用户或可访问同一连接器的账号仍可能调用该固定库，账号分开/目录700不隔离同一个 OS 用户。不要在姐姐账号、成人工作会话或其他专家中启用本连接器；正式儿童独立使用前核对实际可达权限与独立 OS 用户/设备配置。
- 若关掉本连接器，聊天与当前页帮助仍可继续；原生记忆另行管理。不改全局记忆开关，不索要密钥，不建立HTTP后台服务或自动通知。

官方结构：https://open.workbuddy.cn/docs/expert 。连接器启用与管理：https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Connector 。
