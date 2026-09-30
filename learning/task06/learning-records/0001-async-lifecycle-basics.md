# 异步子 Agent 生命周期基础

用户已经能区分短任务应使用同步委派、长程任务才适合异步后台任务，并理解用户询问进度时必须读取实时状态，而不能相信旧消息。用户还认识到旧 ToolMessage 中的状态可能过时；工具名称需要固定使用 `check_async_task` 和 `list_async_tasks`，避免误写成 sync 版本。

**Status**: active

**Evidence**: Session 0 的三道回忆题中，第 1、3 题独立回答正确，第 2 题的机制判断正确但 API 名称需要校正。

**Implications**: 下一步可以直接进入本地服务实验，重点观察 `start_async_task` 返回 task ID、随后 `check_async_task` 看到 `running` 和 `success`，不再重复讲同步/异步的基本动机。

