# Task 05 与第 9 章：委派和审批

本资料摘自 `learning/task05/README.md` 和 `learning/task07/ch09-human-in-the-loop/learning.md`。

- 同步 `task` 委派会等待子 Agent 完成；子 Agent 的中间工具消息与主 Agent 上下文隔离。
- 敏感工具可以配置 `interrupt_on`，在执行前产生人工审批中断。
- 使用同一个 `thread_id` 和可访问的 Checkpointer 恢复；批准与拒绝后，需要核对实际执行记录。
