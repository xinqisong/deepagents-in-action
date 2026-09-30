# 取消与任务总览实验：LangSmith trace 证据

本次实验通过 LangSmith 项目 `deepagents-task06-async-subagents` 读取，避免依赖被控制台截断的输出。

**Status**: active

**Evidence**:

- 第一个任务：
  - `task_id/thread_id`: `01a0f1d0-5fd4-7fd3-9717-a3388174c991`
  - `run_id`: `01a0f1d0-5fd6-7882-9fc9-b7cbf334a638`
  - 启动时状态为 `running`
  - `cancel_async_task` 的工具结果为 `cancelled`
  - 随后的 `check_async_task` 返回 `interrupted`
  - LangSmith 中该 researcher root 最终为 `error`，错误是 `CancelledError(UserInterrupt('User interrupted the run'))`
- 第二个任务：
  - `task_id/thread_id`: `01a0f1d0-6aa1-7302-88d9-d98cb0420dd3`
  - `run_id`: `01a0f1d0-6aa3-76e3-a0c4-72fdd3f9804b`
  - 启动时状态为 `running`
  - 取消第一个任务后仍保持独立运行
  - 早期 check/list 时仍为 `running`
  - LangSmith 中约 20 秒后最终为 `success`
- 取消前的 `list_async_tasks` 正确看到两个任务，说明两个 task 使用不同的 task/thread/run 身份并行存在。

**Conclusion**:

这次实验同时观察到了四种状态表现：

```text
取消工具结果       → cancelled
check_async_task   → interrupted
被取消的 LangSmith researcher trace → error + CancelledError
未取消的 researcher trace → success
```

这不是控制台丢数据，而是不同层记录不同语义。尤其是未取消任务在早期 list 时仍为 `running`，后来才在 LangSmith 中变成 `success`，证明查询结果还与查询时刻有关。

**Learning outcome**:

本节已完成：`cancel_async_task` 只取消指定 task；另一个 task 可以独立完成；状态必须绑定到工具、服务端 run 或 tracing 来源，不能只看状态字符串。
