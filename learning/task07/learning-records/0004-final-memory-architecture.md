# Learning Record: final memory architecture

## Completion

Task 07 的长期记忆概念和本地实验已完成：

- Checkpointer 与 Store 的生命周期边界；
- thread_id、namespace、key、value；
- CompositeBackend 路径路由；
- Agent 运行时写入与 Store 证据校验；
- user、agent、organization 三种作用域；
- 只读策略、人工审批、审计；
- last-write-wins 与后台整合；
- InMemoryStore 到生产 Store 的升级设计。

## Final architecture

以用户偏好 Agent 为例：

- 短期状态：数据库 Checkpointer，按 thread_id 保存；
- 长期记忆：PostgresStore；
- 用户 namespace：assistant_id、user_id、memories；
- 组织策略 namespace：org_id、policies；
- 用户偏好：用户明确要求时读写，写入后直接检查 Store；
- 组织策略：应用或管理员写入，Agent 只读，敏感变更需要审批。

## Boundary

本章已完成本地实验和生产架构设计，但尚未实际启动 PostgreSQL 或部署 LangSmith。真实生产部署仍需单独验证数据库连接、迁移、权限、备份和故障恢复。

## Status

Task 07 learning complete.
