# Learning Record: production storage design

## Evidence

完成生产化设计题，明确了：

- 长期记忆使用 PostgreSQL-backed Store。
- 短期 thread 状态使用数据库 Checkpointer。
- 用户偏好允许 Agent 在用户明确请求时读写。
- 组织策略由应用或管理员维护，Agent 只读。

## Namespace default

本项目采用：

- 用户偏好：user_id + memories
- 组织策略：org_id + policies

如果同一部署运行多个 Agent，可以进一步加入 assistant_id，避免不同 Agent 共享不应共享的记忆。

## Clarification

用户偏好的“可读写”不是任意写入，仍应要求明确的记忆请求、写入后 Store 校验和必要的审计。

## Next step

进入最终综合设计：为一个生产 Agent 写出完整的 memory architecture decision，包括数据作用域、持久化组件、读写策略、验证证据和失败处理。
