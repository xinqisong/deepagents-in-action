# 实验 1：Checkpointer 的 thread-scoped 记忆

这个实验不调用模型，只用一个 LangGraph 节点把当前消息数量写回去。这样可以把变量缩减为一个：是否复用 `thread_id`。

运行：

```bash
cd learning/task07
uv run python experiment/01-checkpointer/checkpointer_demo.py
```

预期：同一 thread 的第二次调用能看到第一次的消息；新 thread 只能看到自己的输入。
