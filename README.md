# 两个孩子的学习伙伴 · v3

**当前：v0.1 成人验证版已实现，尚未达到儿童直接使用的验收标准。** 家长已于2026-10-27明确授权开始开发并持续推进；不再等待方案确认。

平等、诚实的伙伴：及时帮助孩子跨过作业卡点，一起读当前页、做自己的作品、讨论想法。两人资料独立；不累计代写、不靠打卡留住孩子，也不把人格或动机变成家长报告。

- [批准的完整方案](notes/final-plan-2026-10-27.md)与[工程契约](notes/engineering-plan-2026-10-27.md)
- [当前开发交接，Kimi从此继续](notes/development-handoff-2026-10-27.md)
- [安装与平台验收](workbuddy/final/DEPLOYMENT.md)、[能力账本](workbuddy/final/CAPABILITIES.md)、[本地工具](workbuddy/final/RUNTIME.md)
- [软件验证](validation/v3/software-results.md)、[42组实际情境](validation/v3/scenarios.json)、[实机观察](validation/v3/workbuddy-observations.md)

## 已实现

常驻伙伴规则与六种能力（父母能力单独打包）；Python/SQLite固定身份资料工具；8个有限stdio MCP工具；任务/阅读/自选记忆/愿望单；幂等与版本冲突；原子更正、任务范围忘记、90天清理；带最新撤回/完成状态的恢复；结构化最小导出与Markdown家长摘要；147条去个人化书目候选；可复现的分角色交付包。

48项本地测试通过，包含真实MCP子进程、干净Git归档和解压包运行；最终独立复核通过。GitHub Actions已在Mac/Windows/Linux各通过48项测试和打包：[实际运行](https://github.com/18523102883hao-boop/learning-assistant/actions/runs/40423247956)。这些是软件结果，WorkBuddy实机与儿童体验尚待验证。

## 开发验证

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-mcp.lock.txt
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m companion.bundle --source . --output dist/adult-test-a --child test-a
```

Windows将Python路径换为 `.venv\Scripts\python.exe`。核心无需网络或模型API；真实SDK测试需安装锁定依赖。不得把跳过当通过。

## 尚需完成

WorkBuddy国内账号/监护核对、真实项目规则与Skill加载、拍照/语音纠错、两个OS用户和手机/旧会话权限、自动记忆/历史检索、42组真实模型与平台验收、儿童自然试用。现有成人账号完全访问不作为儿童配置，不以单元测试替代这些门槛。

真实资料、照片、全文、报告、备份和密钥不进Git，也不放运行源码目录。原有Kimi材料与v1/v2历史保留；当前行为以v3为准。课程通读、书目接触范围和方法取舍见[材料审阅](notes/materials-audit-2026-10-27.md)。
