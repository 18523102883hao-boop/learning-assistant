# WorkBuddy 云端伙伴 v1.3.0 · 安装入口

2026-11-01。两份源码与ZIP均为固定分发，可供家长安装和云验收；尚未替两个账号完成实际安装。GitHub发行页：[workbuddy-cloud-v1.3.0](https://github.com/18523102883hao-boop/learning-assistant/releases/tag/workbuddy-cloud-v1.3.0)。使用附加的两个专用ZIP，**不要把GitHub自动生成的Source code ZIP当儿童专家包**，发行tag指向的是此交付文档树，不是两分支合并的专家树。

## 现在怎样操作

1. 先登录沫沫账号，到现有伙伴的维护/修改入口，粘贴[UPDATE-momo.md](UPDATE-momo.md)正文；有相应平台操作工具时由它执行，没有时按它实际指出的界面完成。
2. 再登录一一账号，执行[UPDATE-yiyi.md](UPDATE-yiyi.md)正文，两个账号分开做，不能混用ZIP。
3. 每次都检查真实专家更新、六Skill云上可见、资料关联和新云任务结果；只“已下载”不代表已更新。平台限制哪一步就如实记录未验证。
4. 先由家长试用急求助、要示范、自然聊兴趣、拒记/纠错与阅读退出，再给孩子正常使用；完整清单在包内TESTING.md与源分支validation/cloud-v1.3/。

| 账号 | 包名 | 固定源码 | 安装ZIP |
| --- | --- | --- | --- |
| 沫沫 | learning-partner | [92d573e](https://github.com/18523102883hao-boop/learning-assistant/tree/92d573e83ab8d3c996ab9d02d68b3537b3328980/workbuddy/experts/learning-partner) | [learning-partner-momo-cloud-1.3.0.zip](https://github.com/18523102883hao-boop/learning-assistant/releases/download/workbuddy-cloud-v1.3.0/learning-partner-momo-cloud-1.3.0.zip) |
| 一一 | learning-partner-yiyi | [f7fe615](https://github.com/18523102883hao-boop/learning-assistant/tree/f7fe6152453dbbf9e1bf6f071289c087db7f8abd/workbuddy/experts/learning-partner) | [learning-partner-yiyi-cloud-1.3.0.zip](https://github.com/18523102883hao-boop/learning-assistant/releases/download/workbuddy-cloud-v1.3.0/learning-partner-yiyi-cloud-1.3.0.zip) |

整包SHA见[SHA256SUMS.txt](SHA256SUMS.txt)，逐文件SHA在各包CLOUD-RELEASE.json；机器交接见[release-index.json](release-index.json)。固定commit而非滚动分支用于核验版本。无云管理能力不承诺GitHub触发无人值守升级。

## 这一版实际新增

- 现有6个Skills中加入6张原创数学支架，小三/小五各3；语文证据阅读、保留孩子表达的作文帮助、英语概念解释。立即给有用支持，明确要教就示范；累计代做按整段检查。
- 来源、最近确认时间、有效性、更正与当前相关性的记忆语义，兼容旧档案；自然接续而不采访、不装熟。实际记忆保存仍按平台能力，不虚报。
- 以当前书页/片段为中心、本人阅读位置独立、拒绝跟进就停；不靠漫画剧情引走作业注意力。
- 双包共享21份完全相同的规则/素材文件；保留各自专属agent与槽位。哈希见机器索引。没有引入DeepTutor/题库诊断器/自建记忆服务器，只借鉴经复核的方法。

仍保留147条目录候选、3条已核公开介绍、12条课程方法、113份课程来源索引；这些不是147本全文或全部课程原文。本次没有把家长私人全文资料公开上传。

## 验证范围与已知限制

沫沫14项软件检查通过；一一18项通过、1项旧本机stdio验证因未配置而跳过；0失败。两ZIP可重复构建，整包/逐文件校验通过；防错包、错槽位、篡改与路径逃逸测试通过。软件检查不是孩子对话效果或平台安装证明。50组合成成人场景已备好，全部not_run；实际照片/语音、原生记忆、持久云档案与账号隔离待两个账号实测。实现者两轮静态复核见源分支validation/cloud-v1.3/REVIEW.md；外部双模型审查和正式API评测未运行。

升级不覆盖孩子真实档案、记忆、个人阅读状态或授权，不重导初始兴趣；空模板仅初建。规则回退来源见各包cloud/update-policy.json，平台没有原子回退时不能承诺一键撤销。测试和维护回执留成人私有位置，不把儿童私聊或签名URL上传GitHub。
