# 实验 2：Store 与 namespace 隔离

这个实验不调用模型，直接操作 `InMemoryStore`。它展示长期记忆的最小数据模型：`namespace + key -> value`。

运行：

```bash
cd learning/task07
uv run python experiment/02-store/store_demo.py
```

预期：`user-a` 能读回自己的偏好，`user-b` 读不到同名 key。进程退出后 `InMemoryStore` 的数据会消失，这是刻意保留的开发阶段边界。
