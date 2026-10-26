# 软件验证与审查 · 2026-10-27

## 本地实际结果

环境：macOS26.6.2、Python3.13.7、SQLite3.50.4；mcp1.26.0、pydantic2.12.5、pydantic-settings2.12.0。当前锁定组合真实stdio测试无初始化警告。

` .venv/bin/python -m unittest discover -s tests -q ` 实际输出：

```text
Ran 48 tests in 2.070s
OK
```

没有跳过。本组包括固定绑定、并发/幂等/版本、归因不明、学习证据、阅读独立状态、一次跟进、可选记忆清除、错误撤回、任务完成/忘记防复活、最新清单恢复、真实旧物理库迁移、北京时间去重、结构化摘要过滤/时序/更正、真实CLI新进程与MCP协议、清理/愿望单、角色包隔离、解压源码包运行与可复现哈希。

TDD：各有风险的模块先运行缺实现或回归失败，再实现修复并通过；不是拿镜像实现的断言充测试。另实际完成pip editable安装与A/B两套bundle命令。JSON Schema仅描述形状，语义/权限仍由运行时与平台验证。

## 独立审查

1. 第一轮b16769f发现4项P2和1项P3：事件改写/完成任务恢复/忘记current/读取快照/类型错误；已修复并回归。
2. 第二轮61d31d5确认上述修复，发现报告ID排序、旧物理表未版本化、MCP前置类型检验3项；已修复并回归。
3. 第三轮7e16b0c通过，无新增可复现P1/P2，40项测试含stdio通过。等内容树73adbfc6cd4f9c71ea4e3ca293475958b3e31965，GitHub提交51dff4a517b58a457a8e77859a49075b3e8cf51e可访问。
4. 配置8文件规格审查通过后再质量审查通过；minor回执措辞已精确化。
5. 固定34125ef的末批愿望单、90天清理、分角色打包、部署与CI通过最终只读复核：46项本地与独立源码包测试均通过，无新增可复现P1/P2。
6. 首次CI失败后的修复（下面记录）另做补充复核，不扩大前轮结论。

## CI与未覆盖范围

已配置Ubuntu24.04/Python3.11、Windows2022/Python3.11、macOS14/Python3.13，动作引用固定官方提交，权限contents:read，不读任何模型密钥。首次PR运行40422454819在三系统均失败：打包需要的record-contract.md被旧references/忽略规则漏出提交；Windows另发现locale编码与两处测试sqlite连接未显式关闭。GitHub代码与本地树相同不能发现被忽略文件，故新增干净Git归档验证。

已用继承ASCII环境真实复现UTF-8输入/错误输出失败，增加2项回归后修复：成人CLI与bundle入口显式UTF-8、调用端明确解码、测试连接显式关闭、仅放行该工具合同文件。当前本机48项通过；三系统重跑待收取，尚不声称跨平台通过。原始运行：https://github.com/18523102883hao-boop/learning-assistant/actions/runs/40422454819。

这48项不是42组T情境：没有真实WorkBuddy推理质量、照片/语音、自动记忆/历史、设备OS隔离、手机/旧会话能力或孩子试用证据。工具接口不等于OS沙箱，代码通过不等于儿童可用。G/T状态以CAPABILITIES及真实记录为准。

## 可复现产物

最新本地目录dist/v0.1.0-adult-test-a-r3与dist/v0.1.0-adult-test-b-r3，各有孩子包、父母包、成人运行源码包和release.json。release-manifests.json保留对应SHA256；source-file-hashes.json保存本轮代码/规则/材料合同哈希，避免API提交SHA与本地SHA不同造成范围混淆。二进制可重建，不入Git。

技术依据：[Python文本流编码](https://docs.python.org/3.11/library/io.html#io.TextIOWrapper.reconfigure)、[SQLite连接上下文不负责关闭](https://docs.python.org/3.11/library/sqlite3.html#how-to-use-the-connection-context-manager)。
