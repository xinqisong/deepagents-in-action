# Session 4：部署配置事实核对

用户完成了 ASGI/HTTP 部署边界的第一轮核对。

**Status**: active

**Evidence**:

- `langgraph.json` 同时注册了 `supervisor` 和 `researcher`。
- `graphs/supervisor.py` 中的 `graph_id="researcher"` 与注册键匹配。
- `AsyncSubAgent` 没有配置 `url`，当前实验走同部署 ASGI transport。
- Agent Server 使用 `--n-jobs-per-worker 4`，为 supervisor 和后台 researcher 留出并发槽位。

**Implications**:

下一步进行可恢复的 graph_id 负面实验：只把 `graph_id` 临时改成未注册名称，观察启动任务时服务端的错误边界，然后立即恢复配置。实验重点是确认“注册名错误发生在服务连接/graph 解析层”，而不是把错误误判成 researcher 业务失败。
