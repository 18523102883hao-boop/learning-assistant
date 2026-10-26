# 本地工具安装与成人维护

要求 Python 3.11+。数据核心只有标准库；MCP 依赖版本已固定，并用实际 stdio 子进程验证。**尚未验证 WorkBuddy 能调用或 Windows 文件权限。** 不安装全局后台服务，不监听HTTP端口，不读/上传媒体，不包含模型密钥。

## 开发与本机验证

在源码根目录：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-mcp.lock.txt
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m unittest discover -s tests -v
```

Windows在PowerShell使用 `py -3.11 -m venv .venv`，后续将 `.venv/bin/python` 换为 `.venv\Scripts\python.exe`。安装只从正式Python/PyPI来源；安装失败保留日志，不让孩子处理。

普通 `python -m unittest` 若无SDK会明确跳过MCP用例；不能把跳过算通过。锁文件用于复现当前已测试依赖，升级后重跑；不因为“最新”就默换SDK主要版本。

## 成人初始化一个虚构身份

以下 `/ABS/...` 须由成人替换成**仓库外该OS用户自己的私有绝对路径**。不要原样照抄，也不把真实姓名/生日/学校放入。

```bash
python -m companion init --root /ABS/CHILD-DATA --child test-a --nickname 小松 --grade 5
python -m companion doctor --root /ABS/CHILD-DATA --child test-a
python -m companion context --root /ABS/CHILD-DATA --child test-a --speaker-confirmed
```

新目录才可初始化，已存在拒绝覆盖。身份不符拒绝打开；旧SQLite物理格式拒绝静默写入。早期开发库升级用 `python -m companion migrate --root /ABS/CHILD-DATA --child test-a`，保留原有效副本和最新撤回清单再操作。JSON合同版本3与SQLite物理格式4分别记录，旧同秒事件顺序未知不补造。

MCP启动（先只成人测试）：

```bash
python -m companion.mcp_server --root /ABS/CHILD-DATA --child test-a --materials /ABS/READONLY-MATERIALS/catalog.v3.json
```

它等待stdio客户端，所以直接开终端不会像聊天窗口一样回应。客户端command填该虚拟环境Python的**绝对路径**；args按上述逐项填写，不加shell拼接。缺材料仍可陪读眼前页。SDK版本不符会明确停止。八工具及字段见 learning-log 的 references/record-contract.md；父母导出/恢复/初始化不在儿童MCP工具中。

## 成人摘要和愿望单

用操作系统真实权限隔离的成人流程取得该孩子最小导出后，在父母空间使用。不能让孩子账号跨读父母目录，也不能因此授予跨用户任意权限。

```bash
python -m companion parent-export --root /ABS/CHILD-DATA --child test-a --start 2026-10-26 --end 2026-11-01 --output /ABS/PARENT-PRIVATE/export-v1.json
python -m companion report --root /ABS/CHILD-DATA --child test-a --start 2026-10-26 --end 2026-11-01 --output /ABS/PARENT-PRIVATE/week-v1.md
python -m companion report-status --root /ABS/CHILD-DATA --child test-a --metadata /ABS/PARENT-PRIVATE/week-v1.md
python -m companion wishlist --root /ABS/CHILD-DATA --child test-a
```

report是直接Markdown；元数据放同文件注释以避免正文/版本分离。输出存在时拒绝覆盖。更正版用新文件名，加 `--supersedes report-旧ID`。任何来源变更都会保守地令旧报告过时；工具无法删除家长人工复制件。

程序摘要只用准入知识点标签和行为枚举，未知标签不回显文本；不导出 attempt_summary、记忆正文、暂停点或普通私聊。愿望单只显示 `share_with_parent=true` 的自选候选，不代表下单、读过或跟进许可。

## 备份、恢复、清理

```bash
python -m companion backup --root /ABS/CHILD-DATA --child test-a --output /ABS/PARENT-PRIVATE/backup-new.json
python -m companion deletion-registry --root /ABS/CHILD-DATA --child test-a --output /ABS/PARENT-PRIVATE/deletions-current.json
python -m companion restore --root /ABS/CHILD-DATA --child test-a --package /ABS/PARENT-PRIVATE/backup-old.json --registry /ABS/PARENT-PRIVATE/deletions-current.json --op restore-unique-001 --confirm-current-registry
python -m companion prune --root /ABS/CHILD-DATA --child test-a --op retention-unique-001
```

恢复先应用删除/撤回/任务完成ID，再合并，不覆盖现存较新状态。新设备同样需要来源端最新清单；`--confirm-current-registry` 是成人的实际核查声明，不是算法证明。哈希只校验损坏，不认证来源。清单错误/缺失/来源不符/已知回退会拒绝。

MCP每次启动及成人prune会清理90天外事件/自选偏好，清除正文并留无正文ID防恢复。运行进程关闭时不会有后台清理；长期关机后先清理再使用。未完成任务只保留必要续接状态，完成后清暂停点；家长可主动忘记任务。备份保留最多30天由成人轮换管理，不能连最新删除清单一起丢掉；旧备份仍可能含原文，禁止绕过清单直接加载。

媒体不额外复制；WorkBuddy自身附件/历史保存另验。父母报告由父母管理。所有真实资料、报告、照片、备份和密钥不进Git。

## 交付包

`python -m companion.bundle --source . --output dist/v0.1.0-test-a --child test-a` 生成孩子包、父母包、运行源码包及SHA256。只复制显式允许文件，不把完整仓库、旧候选、课程全文或个人数据塞进孩子包。打包不是安装，更不是儿童可用验收。
