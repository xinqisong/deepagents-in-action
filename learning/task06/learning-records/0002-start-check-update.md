# 启动、查询与更新后台任务

实际运行 task06 的 SDK 实验后，用户观察到 `start_async_task` 立即返回 `task_id`，任务状态为 `running`；随后 `check_async_task` 查询到实时的 `running` 状态；再调用 `update_async_task` 时，`task_id` 和 `thread_id` 保持不变，但 `run_id` 和 `last_updated_at` 发生变化，说明更新是在原任务会话上追加指令，而不是新开一个任务。

**Status**: active

**Evidence**: 2026-09-30 的 `run_demo.py` 输出：任务 ID 为 `01a0f11f-3492-7891-9c8e-7cf59ad4e813`；第一次 `run_id` 为 `01a0f11f-3493-71d1-8941-402fd4d80ad3`，更新后变为 `01a0f11f-4945-72f0-863b-81bad0aaae87`；更新返回成功且状态仍为 `running`。

**Implications**: `start`、`check`、`update` 的生命周期理解已经有运行证据。下一步只需补做同一 thread 上的最终查询，确认 `running → success`，然后学习 `cancel_async_task` 和 `list_async_tasks`。

