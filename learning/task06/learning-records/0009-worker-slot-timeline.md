# worker 槽位实验：单槽位造成请求串行化

本次按 `--n-jobs-per-worker 1` 启动服务后，通过 LangSmith 项目 `deepagents-task06-async-subagents` 读取时间线。

**Status**: active

**Evidence**:

- 第一个任务的 `start_async_task` 在约 `11:07:02.97` 执行并返回 task ID `01a0f1ff-1bbc-70f1-8569-9f6e25460c05`。
- 第一个 researcher run 从约 `11:07:04.19` 运行到 `11:07:27.11`。
- 第二次“启动第二个任务”的 supervisor 请求直到约 `11:07:27.11` 才开始，几乎紧接着第一个 researcher 结束；它不是立即并行进入。
- 第二个任务的 `start_async_task` 在约 `11:07:29.72` 执行，task ID 为 `01a0f1ff-843e-7d72-a46d-2cac1bb859f5`；对应 researcher run 约从 `11:07:31.07` 运行到 `11:07:51.08`。
- `11:07:51` 的 `list_async_tasks` 已看到两个任务为 `success`。
- 随后尝试取消第一个任务时，工具返回 `No matching runs to cancel`，因为它已经完成，不能再取消。

**Conclusion**:

在单 worker 槽位下，第一个后台 researcher 占用执行资源时，后续 supervisor 请求也会被阻塞或排队。因此用户感知到的不是两个任务同时运行，而是第二次操作延迟到第一个任务结束后才开始。槽位不足是容量/调度问题，不是 async task 状态机错误。

**Learning outcome**:

已经通过 LangSmith 时间线观察到 worker 容量对请求顺序的影响，并确认终态任务不能再执行 cancel。
