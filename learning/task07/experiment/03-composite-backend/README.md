# 实验 3：CompositeBackend（下一步）

这里将把前两个实验接到 Deep Agent：

```text
/workspace/draft.txt          -> StateBackend（短期、当前运行）
/memories/preferences.md      -> StoreBackend（长期、跨 thread）
```

计划中的最小闭环：

1. 用 `InMemoryStore` 预置 `/preferences.md`；
2. 用 `CompositeBackend` 把 `/memories/` 路由到该 Store；
3. 通过 `memory=["/memories/preferences.md"]` 加载已有文件；
4. 用全新的 `thread_id` 验证读取；
5. 直接从 Store 检查写入结果。

本实验使用 LangChain 的 fake chat model，不需要真实模型密钥；它只负责让 Agent 完成一次调用，实验重点是检查模型收到的 system prompt 是否包含 Store 中预置的记忆。

运行：

```bash
cd learning/task07
uv run python experiment/03-composite-backend/composite_backend_demo.py
```

预期观察：

- Agent 可见路径是 `/memories/preferences.md`；
- Store 中的 key 是 `/preferences.md`；
- `user-a` 的 namespace 中的内容被加载到 system prompt；
