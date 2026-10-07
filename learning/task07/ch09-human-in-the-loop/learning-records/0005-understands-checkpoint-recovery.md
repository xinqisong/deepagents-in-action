# 能根据检查点状态判断恢复结果

用户在单工具审批实验中实际运行恢复：暂停前执行记录为空；批准后中断数量为 0，执行记录出现一次 `update_preference(language, 中文)`。随后使用 `get_state(config)` 观察到暂停时 `next` 指向 `HumanInTheLoopMiddleware.after_model`，`tasks` 中有待处理 Interrupt；用户预测正常结束后 `next` 与 `tasks` 都会变成空元组，并运行确认。

用户能判断换用新的 `thread_id` 无法找到原任务；面对“同一 ID、新建空 `InMemorySaver`”变体，也判断无法恢复，但最初将原因误说为 ID 不同。已澄清：ID 没变，新的 Saver 不含原检查点。尚未实测跨 Saver 恢复。
