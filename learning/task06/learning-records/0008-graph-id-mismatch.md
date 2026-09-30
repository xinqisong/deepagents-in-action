# graph_id 不匹配：服务连接层失败

本次故意将 `AsyncSubAgent.graph_id` 改为未注册的 `researcher_not_registered`，验证了 graph 注册名错误的边界。

**Status**: active

**Evidence**:

- Agent Server 日志返回：`Invalid assistant: 'researcher_not_registered'`。
- 服务端明确列出允许的注册 graph：`supervisor`、`researcher`。
- 错误发生在 `Failed to launch async subagent` 阶段，说明任务还没有进入 researcher 的业务执行。
- 日志中的 `graph_id=supervisor` 表示当前外层 supervisor graph；`langgraph_node=tools` 表示错误发生在 supervisor 执行工具节点时；它们不是被调用的 researcher graph。
- 当前 `supervisor.py` 已恢复为 `graph_id="researcher"`。

**Conclusion**:

`graph_id` 会作为 Agent Protocol 请求中的 assistant/graph 标识交给服务端解析。它必须是有效 assistant UUID，或 `langgraph.json` 中注册的 graph 名称。名称不匹配时，失败发生在任务启动前，不应把它记录为 researcher 的业务失败。

**Learning outcome**:

已经能够区分“服务连接/graph 解析失败”和“后台 researcher 已启动后的运行失败”。
