# 实验观察记录

> 记录“我观察到了什么”和“我据此能解释什么”，不要只粘贴终端输出。

## 实验 1：Checkpointer 与 thread

- 运行命令：
- 同一 `thread_id` 的现象：
- 换用新 `thread_id` 的现象：
- 证据来自：
- 我的解释（不超过 3 句话）：

## 实验 2：Store 与 namespace

- 写入的 namespace：
- 写入的 key：
- `user-a` 读取结果：
- `user-b` 读取结果：
- 证据来自：
- 我的解释（不超过 3 句话）：

## 实验 3：CompositeBackend（待完成）

- Agent 可见路径：
- 实际 Store namespace：
- 实际 Store key：
- 新 thread 是否读到：
- 失败或版本差异：

## 回忆题

1. Checkpointer 和 Store 的生命周期边界分别是什么？
2. namespace 与 `thread_id` 为什么不能互相替代？
3. 为什么需要直接检查 Store，而不能只相信模型的“已记住”？
