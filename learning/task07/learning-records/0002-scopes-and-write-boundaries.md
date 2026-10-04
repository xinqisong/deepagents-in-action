# Learning Record: scopes and write boundaries

## Context

完成 Task 07 Session 5 的 namespace 作用域实验。

## Evidence

- 能解释 user-scoped 记忆：user-a 和 user-b 即使使用相同 key，也因为 namespace 不同而彼此隔离。
- 能解释 agent-scoped 记忆：多个用户读取同一个 Agent namespace 时，可以共享 Agent 知识。
- 已认识到 namespace 只负责数据分区，不自动阻止写入。
- 能提出人工审核和校验作为组织策略的保护机制。

## Clarification

需要区分四类机制：

- namespace：决定数据属于哪个隔离分区；
- permissions：决定 Agent 是否被允许写某条路径；
- application-managed write：由应用或管理员写入共享策略，Agent 只读；
- human approval：敏感写入先暂停，得到人工确认后再继续；
- tracing/audit：记录发生了什么，但本身不阻止写入。

## Still to learn

- 如何为组织策略配置只读路径；
- deny、interrupt 和普通写入的差异；
- 多线程同时写同一个记忆文件时的冲突和整合策略。

## Next step

进入并发写入与记忆整合实验。
