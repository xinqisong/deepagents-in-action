# Task 04 实验资料：任务规划与中间件

## 1. 为什么需要规划

简单任务可以直接调用一个工具完成。复杂任务通常包含搜索、读取、比较、写作和检查等多个阶段。没有任务清单时，Agent 可能遗漏步骤、重复搜索、在长上下文中失去主线，或者把“调用成功”误认为“任务质量合格”。

## 2. v0.7 中显式启用任务规划

`TodoListMiddleware` 会注入 `write_todos` 工具、`todos` 状态和规划提示词。v0.7 不再默认安装它。单步问答不一定需要规划；长程、多阶段、容易漏步骤的任务，或者 UI 需要显示进度时，才应启用并通过真实任务验证效果。

## 3. Todo 数据与状态

一个任务通常有 `content` 和 `status` 两个字段。状态包括 `pending`、`in_progress`、`completed`，常见流转是 pending → in_progress → completed。模型可以根据新信息增加、删除或调整任务，这不是框架强制的状态机。

`completed` 只是 Agent 写入的进度标记。应用仍需检查报告、文件、引用或测试等真实产物。

## 4. 持久化与上下文管理

`todos` 保存在 Agent State 中，和消息历史分开。对话总结不会自动删除它，但多次 `invoke()` 之间要复用同一个 `thread_id` 并配置 Checkpointer 才能接续状态。`InMemorySaver` 只适合当前进程；跨进程恢复需要持久化 Checkpointer。

任务规划和第 3 章的文件系统互相补位：任务清单记录“还要做什么”，文件系统保存“已经得到的资料和产物”，上下文总结减少本轮模型输入。

## 5. 中间件 Hook 与职责

- Node-style：`before_agent`、`before_model`、`after_model`、`after_agent`，作为图中的生命周期节点，适合校验、状态更新、审计和人工中断。
- Wrap-style：`wrap_model_call`、`wrap_tool_call`，包裹一次模型或工具调用，适合重试、缓存、降级和请求/响应转换。
- `PatchToolCallsMiddleware` 只补齐缺失的工具响应消息，不会重新执行工具，也不证明外部副作用已撤销。
- Retry 中间件按策略重试异常；Checkpointer 保存和恢复运行状态；结果是否正确需要应用自己的校验或人工审核。

## 6. 中间件的配置位置

- 默认能力：`FilesystemMiddleware`、`SummarizationMiddleware`、`PatchToolCallsMiddleware` 等；
- 专用参数：`skills=`、`memory=`、`interrupt_on=`、`subagents=` 等；
- `middleware=[...]`：显式加入 `TodoListMiddleware` 等可选策略。

同名中间件在 v0.7 中会在原位置被替换，不会把新旧配置逐字段合并，因此替换后要重新检查 Backend、权限和子 Agent 行为。

## 7. SummarizationMiddleware 的关键点

LangChain 版本通常在 `before_model` 节点执行；Deep Agents 版本把摘要逻辑放在模型调用的包装层，并把旧消息保存到 Backend，再让本轮模型看到摘要和近期消息。手动实例化时要显式设置 `trigger` 和 `keep`，否则不会按阈值主动摘要。
