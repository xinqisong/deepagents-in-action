# Task 07：长期记忆知识总结

## 一句话总览

Deep Agents 的记忆分成两条链：

- Checkpointer：保存同一个 thread 内的短期状态。
- Store：保存可以跨 thread 读取的长期记忆。

CompositeBackend 决定 Agent 的文件路径应该交给哪个 Backend。

## 1. 短期记忆与长期记忆

| 类型 | 作用域 | 典型内容 | 开发实现 | 生产实现 |
| --- | --- | --- | --- | --- |
| 短期记忆 | thread-scoped | 消息、临时状态、当前任务 | InMemorySaver | 数据库 Checkpointer |
| 长期记忆 | cross-thread | 偏好、项目知识、研究结论 | InMemoryStore | PostgresStore 或托管 Store |

同一个 thread_id 可以恢复之前的对话状态；换一个 thread_id 后，Checkpointer 不会自动共享原来的状态。

thread_id 是状态标识，不是用户权限边界，也不是身份认证机制。

## 2. Store 的数据模型

Store 的基本关系是：

    namespace + key -> value

示例：

    namespace = ("user-a", "memories")
    key = "/preferences.md"
    value = "代码注释使用中文，变量名使用英文"

含义：

- namespace：数据隔离分区，可以代表用户、Agent 或组织；
- key：分区内的一条记忆文件；
- value：记忆文件的实际内容和元数据。

相同 key 不代表相同数据。namespace 不同，数据就可以完全隔离。

## 3. CompositeBackend 路由

Agent 看到的是虚拟文件路径：

    /memories/preferences.md

如果配置了：

    routes = {
        "/memories/": StoreBackend(...)
    }

那么：

    Agent 可见路径：/memories/preferences.md
    路由前缀：      /memories/
    Store key：     /preferences.md

通常的路由设计：

    /workspace/  -> StateBackend
    /memories/   -> StoreBackend
    /policies/   -> 只读的 StoreBackend

对 Agent 来说，读取和写入仍然使用 read_file、edit_file 等文件工具；Backend 决定数据最终存在哪里。

## 4. memory 参数的作用

memory=["/memories/preferences.md"] 表示：

- 启动或调用时尝试加载已有记忆文件；
- 将已有内容提供给 Agent；
- 不代表 Agent 一定会写入这个文件；
- 不代表模型回复“记住了”就一定持久化成功。

记忆文件必须先存在，首次初始化通常由应用代码使用 store.put 和 create_file_data 完成。

## 5. 三种常见作用域

### User-scoped

    namespace = (user_id, "memories")

适合：

- 用户偏好；
- 用户项目上下文；
- 用户个人研究记录。

特点：A 用户的记忆不能被 B 用户读取。

### Agent-scoped

    namespace = (assistant_id, "memories")

适合：

- Agent 的共享知识；
- Agent 的长期工作风格；
- 多次对话积累的专业经验。

特点：多个用户可以共享同一个 Agent 的记忆，因此更需要写入控制和整合。

### Organization-scoped

    namespace = (org_id, "policies")

适合：

- 合规规则；
- 组织级知识；
- 内部安全政策。

特点：多个用户或 Agent 可以读取，但通常不允许 Agent 直接写入。

如果同一部署运行多个 Agent，可以把 assistant_id 也加入 namespace，避免不同 Agent 互相污染记忆。

## 6. 长期记忆写入闭环

可靠的写入流程是：

    用户明确要求记住
            ↓
    Agent 读取旧文件
            ↓
    Agent 使用 edit_file 更新
            ↓
    应用直接从 Store 读取并断言
            ↓
    新 thread 再次读取
            ↓
    观察记忆是否生效

重要区别：

- 模型说“已记住”：只是自然语言回复；
- edit_file 出现在工具调用中：说明 Agent 尝试写入；
- Store 中出现正确内容：才是持久化成功的证据；
- 新 thread 能读取：才证明跨对话记忆生效。

测试模型 Agent 时，不要过度依赖逐字匹配。模型可能把“变量名用英文”改写成“变量命名使用英文”。应检查稳定的事实或关键词，生产系统最好使用结构化数据和校验规则。

## 7. 权限边界

namespace 负责数据分区，不自动负责权限。

### 用户偏好

- 默认可以读写；
- 只有用户明确要求时才写入；
- 写入后检查 Store；
- 必要时记录 tracing。

### 组织策略

- 应用代码或管理员写入；
- Agent 默认只读；
- 使用权限规则拒绝敏感路径写入；
- 敏感变更可以触发人工审批；
- tracing 负责审计，不等于权限控制。

需要区分：

    namespace  -> 谁的数据
    permissions -> 谁可以做什么
    tracing     -> 发生过什么
    human approval -> 是否允许这次敏感操作

## 8. 并发写入

多个 thread 同时修改同一个文件，可能出现 last-write-wins：

    Writer A 读取旧内容
    Writer B 读取旧内容
    Writer A 写入更新
    Writer B 写入更新
    最终可能只剩 Writer B 的版本

降低冲突的方法：

- 按主题拆分记忆文件；
- 每个 thread 先写独立事件文件；
- 后台整合 Agent 定期合并；
- 共享 Agent 记忆尽量不要由所有对话直接修改；
- 对敏感共享内容加入校验和审批。

事件整合模式：

    /events/thread-a.md
    /events/thread-b.md
              ↓
    consolidation agent
              ↓
    /memories/AGENTS.md

热路径写入的优点是立即可用；后台整合的优点是延迟低、能综合多个对话，但记忆要到下一次对话才可用。

## 9. 从开发到生产

### 开发阶段

- InMemorySaver：快速测试 thread 状态，进程结束后丢失；
- InMemoryStore：快速测试长期记忆，进程结束后丢失；
- 优点是零配置，缺点是不持久化。

### 生产阶段

- 数据库 Checkpointer：保存 thread 状态；
- PostgresStore：保存跨 thread 的长期记忆；
- 第一次使用数据库通常需要 setup 初始化表结构；
- 应用启动和关闭时管理数据库连接。

### LangSmith 部署

托管部署可以由平台提供持久化 Store 和 Checkpointer，应用不必手动管理全部数据库连接，但仍然要设计好：

- namespace；
- key；
- 文件组织；
- 读写权限；
- 审计和故障恢复。

生产化不是只替换一个 Store 类，而是同时考虑短期状态、长期记忆、身份、权限、并发和备份。

## 10. 常见错误

### 把 thread_id 当成长期记忆

thread_id 只标识一个对话线程。跨 thread 记忆需要 Store。

### 把 namespace 当成权限

namespace 只能隔离数据。只读策略还需要权限规则、应用层写入或人工审批。

### 只相信模型回复

模型可能声称写入成功，但工具调用失败或写入了错误路径。必须直接检查 Store。

### 把 Agent 路径直接当 Store key

挂载了 /memories/ 路由后，Store key 通常要去掉这个路由前缀。

### 生产环境继续使用内存 Store

InMemoryStore 适合本地开发，不适合需要重启后保留数据的服务。

## 11. 排障清单

遇到长期记忆问题时，依次检查：

1. 当前观察的是 Agent state、Store item、run 还是 tracing？
2. thread_id 是否符合预期？
3. user_id、assistant_id、org_id 是否来自可信运行时上下文？
4. namespace 是否正确？
5. Agent 路径和 Store key 是否多了一层路由前缀？
6. 记忆文件是否预先存在？
7. 是否真的出现了 read_file 或 edit_file 工具调用？
8. Store 中的内容是否真的更新？
9. 是否用新的 thread_id 验证了跨对话读取？
10. 是否把模型的自然语言输出误当成了持久化证据？

## 12. 本章最终心智模型

    当前对话继续
        -> thread_id
        -> Checkpointer
        -> 短期状态

    新对话仍然记得
        -> namespace
        -> Store
        -> 长期记忆

    文件操作走向哪里
        -> CompositeBackend
        -> 路径路由

    谁能看到、谁能修改
        -> namespace + permissions + application policy

    多个对话如何安全更新
        -> 拆分文件 + 事件记录 + 后台整合

    如何走向生产
        -> 数据库 Checkpointer + PostgresStore 或托管平台

参考资料：

- Datawhale 第 8 章：
  https://datawhalechina.github.io/deepagents-in-action/chapters/ch08-long-term-memory/
- Deep Agents Memory：
  https://docs.langchain.com/oss/python/deepagents/memory
- LangGraph Memory：
  https://docs.langchain.com/oss/python/langgraph/add-memory
