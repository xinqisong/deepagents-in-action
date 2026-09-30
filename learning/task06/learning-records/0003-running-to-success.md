# 后台任务从 running 到 success

用户完成了 task06 最小生命周期实验，并取回了后台 researcher 的最终结果，验证了异步任务可以在 supervisor 返回后继续运行，随后通过同一任务引用取得终态结果。

**Status**: active

**Evidence**: 用户反馈已成功取到最终结果；此前输出已经验证 `start_async_task`、`check_async_task`、`update_async_task`，本次补齐了 `running → success`。

**Implications**: 可以进入取消与任务总览实验，重点学习 `cancel_async_task` 的最终一致性，以及 `list_async_tasks` 与单任务 `check_async_task` 的职责差异。

