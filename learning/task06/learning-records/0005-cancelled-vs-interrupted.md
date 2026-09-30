# `cancelled` 与 `interrupted` 的状态来源

本次纠正了一个重要的教学和排障误区：取消工具的确认、Agent Protocol 服务端某次 run 的状态、LangSmith tracing 中的结束状态，不是同一个字段。

**Status**: active

**Evidence**:

- 当前本地环境为 `deepagents==0.7.19`、`langgraph==1.2.12`、`langgraph-sdk==0.4.5`。
- 本地 `deepagents/middleware/async_subagents.py` 中，`cancel_async_task` 在 `runs.cancel()` 成功后将 supervisor 的 `async_tasks[task_id].status` 写为 `cancelled`。
- 同一文件中，`check_async_task` 每次都会读取服务端的 `run.status`，然后用这个原始状态更新 supervisor 的任务记录；因此后一次 check 可能把记录从 `cancelled` 改成服务端返回的 `interrupted`。
- `update_async_task` 在同一个 thread 上创建新 run，并使用 `multitask_strategy="interrupt"`；旧 run 被中断、新 run 获得新的 `run_id`，而 `task_id` 保持不变。
- [官方 Async subagents 文档](https://docs.langchain.com/oss/python/deepagents/async-subagents) 将 cancel 描述为调用 `runs.cancel()` 并把任务标记为 `cancelled`，同时说明 update 会中断旧 run。
- [官方 middleware 源码](https://github.com/langchain-ai/deepagents/blob/main/libs/deepagents/deepagents/middleware/async_subagents.py) 是 API 行为的实现依据；[官方 issue #3008](https://github.com/langchain-ai/deepagents/issues/3008) 还记录了 `interrupted` 的处理和精确 resume 目前存在的边界。

**Conclusion**:

用户在 tracing 中看到最终 `interrupted`，而取消工具当时显示 `cancelled`，两者可以同时成立。前者描述被观测的具体执行过程被打断，后者描述取消动作对任务跟踪状态的确认。若随后调用 `check_async_task`，它可能用服务端 run 的 `interrupted` 覆盖 supervisor 中原来的 `cancelled`。

**Teaching correction**:

以后不能只说“取消后的最终状态是 `cancelled`”。正确说法是：先看取消工具的确认，再用同一个 `task_id/thread_id/run_id` 分别核对 check/list、服务端 run 和 tracing；报告状态时必须注明来源。课程原文和概念图用于建立模型，具体状态以当前官方文档、当前安装版本源码和实际运行证据为准。
