# Mission: Deep Agents 长期记忆

## Why

把第 7 章学到的 Skills 能力继续向前推进：让 Agent 不只记得当前对话，还能在新的 thread 中安全地读取用户偏好、项目知识和研究进度，并且能解释这些信息为什么没有串给别的用户。

## Success looks like

- 能用自己的话解释短期记忆、长期记忆、Checkpointer、Store 和 `CompositeBackend` 的边界。
- 能用一个可重复的实验验证：相同 `thread_id` 能恢复状态，不同 `thread_id` 不能直接共享 Checkpointer 状态。
- 能用 `InMemoryStore` 写入并读取记忆，并用不同 namespace 验证用户隔离。
- 能配置 `/memories/` 路由，让 Deep Agent 在新的对话中加载已有记忆文件。
- 能把“模型说它记住了”和“Store 里确实写入了”分开验收。
- 能说明 `InMemoryStore`、`PostgresStore` 和 LangSmith 部署之间的升级关系，以及并发写入、只读策略和敏感记忆的风险。

## Constraints

- 中文互动；每次只推进一个可观察行为。
- 先用本地内存实现建立心智模型，再接入模型和 CompositeBackend。
- 优先核对当前官方文档和本地锁定版本；课程示例若与当前 API 不同，记录差异。
- 不提交真实密钥；实验数据使用虚构的用户和偏好。

## Out of scope

- 本轮不实现向量数据库、复杂语义检索或生产级记忆整合服务。
- 不把“能调用 `store.put`”当作完成标准；必须能解释 namespace、路径路由和跨 thread 验证。
