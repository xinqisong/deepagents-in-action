# 第 9 章：Human-in-the-Loop 互动学习计划

当前分支：`learning/task07`。本目录是第 9 章的教学工作区。

当前状态：**核心审批流程已验证成功**（2026-10-07）。用户已核对模拟发布的批准与拒绝结果，见[记录 0008](learning-records/0008-verifies-capstone-demo.md)。`when` 条件、并行中断 ID 和子 Agent 审批仍待专项实践；综合策略由教师填写，尚不记为用户独立设计能力。

## 起点与目标

你已完成第 8 章，能区分 Checkpointer、Store、namespace、权限和审批；第 7 章也做过个人 Skill 的人工批准。依据是上级目录的 `learning-records/0004-final-memory-architecture.md` 和 task06 的审批记录，不重复这些基础实验。

暂定实践目标：把之前提出的“敏感变更需要人工审批”落实成可检查、可恢复的工具调用流程。已询问本章侧重点，收到回答后确定 MISSION.md；此计划可先作为全章地图。

## 全章地图

工具请求 → 判断审批策略 → 暂停并保存状态 → 人工决定 → 恢复 → 检查执行证据

| 节次 | 知识与技能 | 你的练习 | 通过标准 | 预计时间 |
| --- | --- | --- | --- | --- |
| 1. 暂停在哪里 | 请求、审批、实际执行的边界；`interrupt_on` 的配置入口 | 根据一次暂停返回值预测工具是否执行 | 能说出结论与应检查的证据 | 5–10 分钟 |
| 2. 做出决定 | `approve`、`edit`、`reject`、`respond`；`allowed_decisions` | 每轮只补一个 decision；分别观察模拟执行记录 | 能区分拒绝操作和人工提供工具结果 | 15–20 分钟 |
| 3. 找回暂停任务 | 同一 `thread_id`、同一可访问的 Checkpointer；`Command(resume=...)`；返回格式 | 补恢复调用，读取 `get_state(config)`，预测换 thread 的结果 | 用待处理中断和执行记录判断是否完成 | 15–20 分钟 |
| 4. 多个审批请求 | 批次内 action 顺序；并行 Interrupt ID；条件 `when`；子 Agent 策略 | 先处理同批两个 action，再做独立并行中断变体 | 不混淆 action 索引与 Interrupt ID | 20–25 分钟 |
| 5. 恢复如何执行 | 底层 `interrupt()`；节点重放；幂等；调用顺序；异常传播 | 预测并观察计数器在暂停前后的值，再修正一个副作用位置 | 能解释为什么“放在审批后”仍不等于所有故障下恰好执行一次 | 15–20 分钟 |
| 6. 放回现有 Agent | 自定义 Middleware 审稿；文件权限触发审批；输入验证；静态调试断点 | 为虚构的个人偏好变更设计审批，复用上一章的读写证据思路 | 能选对审批层、处理再次中断、说明进程重启时的持久化条件 | 20–30 分钟 |

时间是估算，可以拆成多次对话。每节按“短解释 → 预测 → 补一个缺口 → 观察 → 解释变体”的顺序推进。

## 实验安排

按用户当前偏好，暂停与恢复实验直接使用 task07/.env 配置的真实模型；保留内存执行记录，便于核对审批前后是否调用工具。第一轮只使用模拟写入，不发送真实邮件或删除真实文件。真实模型可能不发起预期调用或再次中断，需要依据输出判断。

不会一次生成全部实验答案。每次按你的回答生成下一份短课与小段代码；完整解答用于反馈或排错。运行成功后仍需解释关键现象，才记为掌握。

## 本次入口

- [第一课：工具请求是否已经执行？](lessons/0001-request-vs-execution.html)
- [第二课：批准原参数执行](lessons/0002-approve-tool-call.html)
- [第三课：拒绝后让 Agent 知道下一步](lessons/0003-reject-with-feedback.html)
- [第四课：修改参数后执行](lessons/0004-edit-tool-arguments.html)
- [第五课：人直接提供工具结果](lessons/0005-respond-as-tool-result.html)
- [第六课：实际暂停与恢复](lessons/0006-resume-one-call.html)
- [第七课：同批两个审批动作](lessons/0007-two-actions-one-batch.html)
- [第八课：恢复时节点重放](lessons/0008-interrupt-node-replay.html)
- [第九课：让副作用经得起重放](lessons/0009-idempotent-side-effects.html)
- [第十课：综合审批练习](lessons/0010-capstone-approval.html)
- [边界速查](reference/hitl-boundaries.html)
- [资源与版本记录](RESOURCES.md)

当前状态：用户已完成单工具审批恢复实验，并通过 `get_state(config)` 验证暂停前有待处理任务、正常结束后 `next` 与 `tasks` 均为空，见记录 0005。同批两个动作实验也已运行，见记录 0006。用户正确预测 `interrupt()` 前代码在首次暂停与恢复时共执行两次、后面代码执行一次，见记录 0007。模拟发布综合练习已按用户要求由教师填写并用真实模型演示：批准后内存记录有一次发布，拒绝后记录为空。它证明演示脚本可用，不作为用户独立配置审批策略的证据；短课编号与计划节次不要求一一对应。

## 保持记忆

下次学习开始用一分钟回忆上一节的新边界；若隔天继续，先做一个小变体。只针对本章新知识安排检索练习，已明确掌握的旧实验不重跑。完成第 6 节后，用一个不同工具场景检验迁移能力。

## 主资料

[课程第 9 章](https://datawhalechina.github.io/deepagents-in-action/chapters/ch09-human-in-the-loop/) 提供章节范围；API 语义分别核对 [Deep Agents HITL](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop)、[LangChain HITL](https://docs.langchain.com/oss/python/langchain/human-in-the-loop) 与 [LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)。
