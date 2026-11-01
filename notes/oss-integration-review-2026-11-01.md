# Hermes 开源调研复核与 WorkBuddy 融合建议

日期：2026-11-01。当前交付是研究复核与实施规格，不是已发布的新专家版本。沿用家庭已确定路线：两个独立 WorkBuddy 账号、云端优先、平等有趣的长期伙伴、阅读与创作优先，不做整页批改/口语评分，不强迫每日练习或教回。

## 1. 当前项目与新增成果的位置

Hermes 的两份成果位于 `research/oss-landscape-2026-11-01`，本轮读取固定提交 `10c8552dbf9cc01e5e80bd882cfa469781be8af0`：`oss-landscape-2026-11-01.md` 与 `taxonomy-coverage-report-2026-11-01.md`。本目录保留原稿，不静默改写原作者结论；本复核覆盖有差异的建议。

GitHub 的 main 当前仍为839325f；两孩子可分发云源码分别在 experts/learning-partner-momo（9754f247b77529bc3e2ffd4b7a092e409220611e）与 experts/learning-partner-yiyi（26242d97da8482f7c675bff321eb16f76150af48），都是1.2.0配置。它们已含六个Skill、147条候选书目、3条核验公开介绍、12条教育方法、113份课程来源索引，以及云项目指令/资料合辑/空白伙伴档案。仓库版本不代表两个真实云账号已更新到该版；本轮未取得家庭云验收记录。

现有六Skill已覆盖作业、阅读、探索、闲聊、记录和资料。新增开源成果宜融入这些入口，不再给孩子增加一排工具，也不迁回本机 Python/SQLite。

## 2. 借鉴优先级与接入形态

| 项目 | 本轮核实的价值 | 融入当前专家的具体方式 | 当前不作为依赖的部分 |
| --- | --- | --- | --- |
| [OATutor](https://github.com/CAHLR/OATutor) | 有独立提示/支架组件、知识追踪实现 | 给 homework-help 增加按卡点选择的提示/图示/概念/示范素材卡，并检查整段累计代做 | React教学平台、LTI/Firebase、掌握门槛和求助惩罚逻辑不移入 |
| [cn-math-taxonomy](https://github.com/xiaoyang111222/cn-math-taxonomy) | 小三/小五数学目录、先修关系与少量题目可作为检索候选 | 先核教材，再选少量常见知识点做“可能的前置卡点”只读索引；关联真实尝试，未知保持未知 | 不把整套诊断器/祖先掌握推断移入，不要求孩子跑完诊断 |
| [DeepTutor](https://github.com/HKUDS/DeepTutor) | README确有learner/guardian、共享书与私人学习状态、可检查记忆的版本说明 | 参考来源—事实—综合结论的呈现，以及书页/片段引用、每人独立阅读状态 | 不在WorkBuddy安装Docker/Python/Node系统，不因此另建账号和服务器 |
| [Learning Commons Evaluators](https://github.com/learning-commons-org/evaluators) | 有讲解反馈、是否泄露答案、适龄等评价提示及SDK | 将有关“反馈是否具体、是否有帮助、是否过量”的维度改写成中文成人评测表 | 英语年级公式不直接打中国小学生分；模型评委分数不是客观掌握证据 |
| [hermes-edu-skills](https://github.com/hezkvectory/hermes-edu-skills) | 场景目录与中文工作流模板，声明外部工具依赖 | 挑对现有六Skill有增量的中文场景，改写/去重后使用 | 不整包导入170个Skill；context.load、workflow.create、memory.write等不能假装WorkBuddy已提供 |
| [promptfoo](https://github.com/promptfoo/promptfoo) | 开发侧模型/提示评测工具，可配自己的provider | 以现有场景先建立合成对话回归格式；有正式API或可用适配器时再跑自动评测 | 不从聊天会员推断API额度，不把本机模型跑分当WorkBuddy云端验收 |

这是机制与素材组织的借鉴建议，并非已复用上述代码。后续若直接复制代码、题目或评价内容，记录具体文件、固定提交、修改和适用许可证。

## 3. Hermes 结论需要校准的地方

1. **“全部教育项目单学生、没有家长角色/多用户隔离”不能成立。** Hermes 自己的DeepTutor章节已经列出learner/guardian与per-user隔离；本轮README也有对应版本记录。只能说没有确认一个能原样满足全部家庭要求的现成组合，不能宣称整个生态空白。[DeepTutor README](https://github.com/HKUDS/DeepTutor/blob/f7aed0744c36c5afef16a4261c31ebee1208cac2/README.md)
2. **关闭一个答案提示开关不能保证WorkBuddy永不输出答案。** 所读OATutor配置实际为 `ENABLE_BOTTOM_OUT_HINTS = true`，不是报告所称开关已经关闭。它控制自己的UI；迁成文本后没有同等程序约束。当前项目允许词义、概念和必要示范直接讲解，应保留这一点，不机械“永远不答”。[配置](https://github.com/CAHLR/OATutor/blob/e24c8456e5f75c07b6048159ea9e128b036f673d/src/config/config.js)、[提示组件](https://github.com/CAHLR/OATutor/blob/e24c8456e5f75c07b6048159ea9e128b036f673d/src/components/problem-layout/HintSystem.js)
3. **BKT是带参数假设的估计，不是客观掌握事实。** 代码由初始掌握、猜测、失误和学习转移参数更新概率。它可以研究，但不能把0.42→0.81展示成两个孩子已经真实提升的证据；当前缺校准样本，不引入掌握百分比或通关门槛。[BKT实现](https://github.com/CAHLR/OATutor/blob/e24c8456e5f75c07b6048159ea9e128b036f673d/src/models/BKT/BKT-brain.js)
4. **mastery_criteria不能填入independence_evidence。** 前者是预期标准，后者是当次观察的证据字段。topicId也需经过当前知识标签/家长摘要映射，不是塞进标签就自动形成可读报告。保留“获得过提示”“仅自报”“未经核对”等边界。
5. **知识图谱的先修边只是候选关系。** 实际engine在目标答对后会将祖先标成mastered/src=inferred。我们不采用该推断：只在当前尝试支持时记录有限结论，不因会做后项就把全部前项标掌握，也不因一次错题断言低年级知识塌陷。[engine](https://github.com/xiaoyang111222/cn-math-taxonomy/blob/dc764bddace4b0918a50f8cb5acec289887e5f5f/diagnose/engine.js)
6. **verify字符串不是全面正确性保证。** 本轮12135题中567条无有效verify字段。所读judgeNumeric主要比较answer/accept及解析结果，未见使用verify字段执行校验；题意、参考答案和表达式本身也需要核查。未来有限计算器应使用审查过的运算白名单，不直接eval下载数据。
7. **学习质量评分仍可能由模型生成。** 所读适龄提示明确针对English literature K–12，并使用Flesch-Kincaid英文词/音节公式；不能直接给中文阅读判年级，更不能当孩子智力/能力评分。[适龄提示](https://github.com/learning-commons-org/evaluators/blob/f03eec9e244e53810d1da3bc065cf38e0c09db0a/evals/text-complexity/ela-reading/grade-level-appropriateness/system.txt)
8. **许可证要分内容和代码。** OATutor代码LICENSE为MIT，README说明教学内容CC BY 4.0、单项JSON另有署名；Evaluators代码MIT、评价内容CC BY 4.0、部分标注数据集CC BY-NC-SA 4.0；taxonomy为CC BY-NC 4.0。后续逐项保留署名和条款，不把仓库一个标签当全部素材同许可。[OATutor说明](https://github.com/CAHLR/OATutor/blob/e24c8456e5f75c07b6048159ea9e128b036f673d/README.md)、[Evaluators许可](https://github.com/learning-commons-org/evaluators/blob/f03eec9e244e53810d1da3bc065cf38e0c09db0a/LICENSE.md)、[taxonomy许可](https://github.com/xiaoyang111222/cn-math-taxonomy/blob/dc764bddace4b0918a50f8cb5acec289887e5f5f/LICENSE)

“每天20题只够10天”是题量算式，不是本家庭需求。当前重点是孩子主动求助、自由阅读和持续陪伴，不为消耗题库设每日练习任务。

## 4. 本轮实际数据复核

固定taxonomy版本dc764bddace4b0918a50f8cb5acec289887e5f5f，直接读取三个JSON，未执行上游代码或verify字符串：

- 2997知识点、4456先修边、12135题；知识点ID无重复、边与题目的引用无悬空。
- 三年级数学51点/204题，五年级数学52点/208题；数学按上游subjectOf所用cnm_前缀与grade筛选，不能假设所有topic都有subject字段。
- 三年级数学choice54/numeric150，五年级choice46/numeric162；未观察到这些子集中的开放过程题。
- 全体每点4题2850个、5题147个；567题无有效verify。

上述统计核对Hermes部分数量结论，不证明题目正确、教材对齐、诊断有效或教育效果。尚未对每道题人工验算，也没有两孩子实测。

## 5. 建议下一版如何改（暂拟1.3，尚未发布）

第一批只改现有Skill与随包资料，不增服务器、不更换入口：

- homework-help：首批选6个示范卡（小三3个、小五3个），卡内区分适用情境、可能的知识关系、一个即时有用的提示、可选图示/具体表示、必要示范、孩子可拒绝的自测与证据边界。以当前题目与教材页核对，不固定年级门槛。每次只取所需小片段，不连问整张诊断表。
- 语文：阅读理解先找原文支持；作文从孩子真实想法与局部表达入手，不多轮拼成可交成稿。英语词义/语法可直接解释，未核教材只做通用帮助。
- partner-chat与learning-log：伙伴档案保持兴趣—作品—阅读—生活—学习五类；新增来源、最近确认、当前/待核/已更正与相关性字段规范。自然提起一个确有依据的过去细节，不每次展示记忆清单。继续用WorkBuddy原生云记忆，独立账号是当前范围基础；没有理由仅为装开源记忆库就再建一套服务。
- reading-companion：借鉴按当前页面/片段讨论与私人阅读状态；保持147候选与113课程来源基线，逐次补充核验书介，不一次换成未经核验的大书库。没有真实去重服务时不承诺一次主动跟进。
- 成人评测：改编“有用性、准确、帮助量、是否累计代做、中文适龄、是否尊重退出、是否自然接续”七个维度。先使用合成对话，评分用来审查AI表现，不给孩子打分。

先验证作业求助、示范跳级、同题多轮代写、AI讲错撤回、非本人代问、记忆更正、自由聊漫画不强转学习、阅读拒绝跟进这8类，再回归现有42组。单元测试不能验证对话效果；外部API自动评测与真实WorkBuddy云任务分别记录。

## 6. GitHub读取与自动更新：可做哪一层

官方能力核验另见 [workbuddy-github-update-feasibility-2026-11-01.md](workbuddy-github-update-feasibility-2026-11-01.md)。

**可以准备并逐账号验证的方案：家长触发一次维护任务，WorkBuddy从GitHub读取固定版本，执行其确有权限的更新步骤。** 当前没有足够公开依据承诺GitHub push后两个云账号无人值守升级。Open API可创建任务，但任务成功创建不等于专家发布成功。

建议每版发布：固定commit、目标专家包名、适用账号槽位、版本、文件SHA、完整包、变更清单、回退源版本、维护提示词。发布包只含规则/方法/书目与空白初建模板；现有伙伴档案、账号记忆、个人阅读状态和凭据不覆盖、不回传GitHub。分支不是访问权限边界。

每个账号更新分为六个独立状态：github_readable → artifact_verified → expert_updated → cloud_skills_visible → library_linked → new_task_verified。每项有实际来源/工具回执或新任务读取证据；没有证据为not_verified。没有真实云管理接口的步骤必须让家长在对应界面完成，不能把云沙箱解压、生成安装说明或模型自述当完成。

同一家庭共用核心规则，各包只覆盖昵称、年级线索、兴趣种子与槽位，避免两分支长久漂移。构建后校验两包公共文件哈希；升级时读取已安装对象，避免更新错专家。失败保留旧版本并报告实际部分结果；没有已验证回滚操作不承诺原子回退。

## 7. 后续处理与需要家庭配合的范围

接下来可按上述第一批规格，修改两个包并制作待成人验证的候选版；验证后分别从各账号维护任务更新。现阶段不需要购买云服务器、配置mem0、迁移DeepTutor或给孩子增加独立学习门户。

家庭侧需要的真实资料：每孩子当前所用教材的版次/册次/目录线索，以及各云账号能否读取私有GitHub、修改专家、选择项目Skill和持续更新档案的实际结果。现有两账号已经准备好，无需重新注册或把登录信息发给开发AI。

本轮已复核6个重点仓库的README、许可或关键源码，未运行这些完整产品；其他Hermes候选未逐仓复核。报告不是全面儿童安全认证、许可证法律意见或安装成功证明。旧专家版本和真实记忆本轮未修改。
