# Task 07 学习计划：长期记忆与 CompositeBackend

本计划对应课程第 8 章。建议分 7 次完成，每次 30～90 分钟；下一次开始前，先用 3 分钟回忆上一次的结论，不要直接翻答案。

## 先建立总地图

```text
同一 thread 的连续对话
        │
        ▼
Checkpointer ──保存 Agent state──► 短期记忆

不同 thread / 不同会话
        │
        ▼
Store + namespace ──保存记忆文件──► 长期记忆
        │
        ▼
CompositeBackend ──按 /memories/ 路由──► Deep Agent 的文件工具
```

核心判断：`thread_id` 解决“这次对话接着上次状态继续”，namespace 解决“不同主体之间哪些长期数据可以共享”。

## Session 0：和前面章节接轨（20～30 分钟）

目标：说清楚本章新增的不是“更多聊天历史”，而是跨 thread 的持久化数据。

动作：

1. 阅读 [第一课](lessons/0001-memory-boundaries.html)。
2. 打开 [长期记忆速查页](reference/long-term-memory-reference.html)，先遮住“答案”部分。
3. 不看资料回答：`thread_id`、Checkpointer、Store、namespace 各自解决什么问题？

验收：能画出“同一 thread”和“新 thread”两条路径，并指出哪一步会用到 Store。

## Session 1：只观察 Checkpointer（30～45 分钟）

目标：亲眼看到短期记忆是 thread-scoped 的。

```bash
cd learning/task07
uv sync
uv run python experiment/01-checkpointer/checkpointer_demo.py
```

验收：记录同一 `thread_id` 的第二次调用如何看到历史，以及换成另一个 `thread_id` 后为什么从空状态开始。证据来自脚本输出，不来自猜测。

产出：填写 `experiment/observations.md` 的“实验 1”部分。

## Session 2：只观察 Store 与 namespace（30～45 分钟）

目标：把长期记忆理解成“带 namespace 的 key-value 数据”，而不是神奇的模型记忆。

```bash
uv run python experiment/02-store/store_demo.py
```

验收：

- 能读回 `user-a` 的记忆；
- `user-b` 读不到 `user-a` 的同名 key；
- 能解释为什么“同名文件”不等于“同一份记忆”。

产出：记录 namespace、key、value 三者的关系。

## Session 3：接入 CompositeBackend（60～90 分钟）

目标：理解 Agent 看到的 `/memories/preferences.md` 如何映射到 Store 中的相对 key。

动作：

1. 复读课程“CompositeBackend：长期记忆的核心方案”和官方 Memory 文档。
2. 在 `experiment/03-composite-backend/` 中补充当前版本可运行代码。
3. 先用应用代码 `store.put(..., create_file_data(...))` 预置一份虚构偏好，再让 Agent 读取；不要一开始测试模型自主写入。

验收：能够指出以下两条边界：

- `/workspace/draft.txt` 走临时 StateBackend；
- `/memories/preferences.md` 走 StoreBackend，并由 namespace 决定隔离范围。

## Session 4：跨对话读写闭环（60～90 分钟）

目标：完成“对话 1 写入 → Store 断言 → 新 thread 读取”的闭环。

建议场景：用户说“记住我喜欢中文注释、英文变量名”。

验收必须分成两部分：

1. 直接从 Store 读取并断言内容确实存在；
2. 使用全新的 `thread_id` 再请求 Agent，检查它读取到的记忆是否生效。

注意：模型回复“已记住”不是写入证据；写入证据来自 Store item 或 tracing 中的工具调用。

## Session 5：作用域、权限与并发（45～60 分钟）

目标：能为 Agent-scoped、User-scoped、Organization-scoped 记忆选择边界。

用表格比较：

| 场景 | 推荐 namespace | 默认写入策略 |
| --- | --- | --- |
| 用户偏好 | `user_id + memories` | 用户请求后读写 |
| Agent 知识 | `assistant_id + memories` | 受控读写或后台整合 |
| 组织策略 | `org_id + policies` | 应用写入，Agent 只读 |

验收：针对“组织合规规则”和“用户个人偏好”各写一个风险说明，并说明为什么不能只靠 system prompt 做权限控制。

## Session 6：从开发走向生产（30～60 分钟）

目标：理解升级路径，而不是立即搭建所有基础设施。

阅读官方文档对应的 `InMemoryStore`、`PostgresStore` 和 LangSmith 部署部分，完成一张对比表：数据是否跨进程、初始化成本、适合场景、失败时的排查入口。

验收：能解释为什么本地实验适合 `InMemoryStore`，生产环境需要数据库或托管平台；能说出迁移时不能改变的 namespace 和 key 契约。

## Session 7：小型毕业实验（90～120 分钟）

目标：做出一个“用户偏好记忆 Agent”，并用可检查证据验收。

最小要求：

1. `UserContext` 明确提供 `user_id`；
2. `/memories/preferences.md` 路由到 StoreBackend；
3. 预置文件，完成一次写入或编辑；
4. 用 Store 直接断言内容；
5. 用新的 thread 读取；
6. 用另一个 user_id 验证隔离；
7. 把失败现象、状态来源和版本差异写入 `learning-records/0001-*.md`。

## 间隔复习与完成标准

每次实验结束后立即回答一个问题，第二天再回答一次：

> 如果换了 `thread_id` 仍然想保留用户偏好，应该增加什么组件？如果换了 `user_id` 却读到了旧偏好，优先检查什么？

本章完成不是“脚本运行成功”，而是你能用自己的话解释：状态保存在哪里、谁能读到、如何证明真的写入、如何避免跨用户泄露。
