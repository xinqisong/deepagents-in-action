# Learning Record: long-term memory read-write boundary

## Context

完成 Task 07 的 Checkpointer、Store、CompositeBackend 和长期记忆写入实验。

## Evidence

- 能区分 thread_id 与 namespace：thread_id 标识对话线程，namespace 隔离长期记忆的主体范围。
- 能解释 Agent 可见路径与 Store key 的关系：/memories/preferences.md 路由后对应 /preferences.md。
- CompositeBackend 实验观察到预置 Store 内容被加载到 Agent 的 system prompt。
- 写入实验中实际观察到 read_file → edit_file → read_file。
- Store 中确实出现了用户偏好；最初的断言因为过度依赖模型措辞而失败，改为检查稳定语义后通过。
- 认识到模型回复“已记住”不是持久化证据，Store 中的实际内容才是写入证据。

## Key insight

LLM 输出是自然语言，测试应断言稳定的业务事实或结构化数据，不应要求模型逐字复述输入。长期记忆实验至少要分别验证：写入工具调用、Store 内容、全新 thread 的读取。

## Still to learn

- Agent-scoped、User-scoped、Organization-scoped namespace 的选择。
- 组织策略的只读边界与权限控制。
- 多线程并发写入、last-write-wins 和后台整合。
- InMemoryStore 到 PostgresStore 或托管平台的升级路径。

## Next step

进入学习计划 Session 5：作用域、权限与并发。
