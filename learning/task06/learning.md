# Task 06 学习记录：异步子 Agent 与并行编排

本次学习对应课程第 6 章“异步子 Agent——让主 Agent 同时驱动多个子任务”。

课程原文：

<https://datawhalechina.github.io/deepagents-in-action/chapters/ch06-async-subagents/>

章节源码：

<https://github.com/datawhalechina/deepagents-in-action/blob/main/content/ch06-async-subagents.md>

## 一、本章目标

完成本章后，我应该能够：

1. 用自己的话解释同步 `task`、异步 `AsyncSubAgent`、Python 协程和“并行编排”之间的区别；
2. 使用 `AsyncSubAgent` 配置 `name`、`description`、`graph_id`，并能判断何时使用 `url` / `headers`；
3. 说清 `start_async_task`、`check_async_task`、`update_async_task`、`cancel_async_task`、`list_async_tasks` 的职责和使用时机；
4. 画出“主 Agent—Agent Protocol 服务—后台 thread/run—用户”的异步生命周期；
5. 用 `langgraph.json` 注册主图和子图，用 `langgraph dev` 启动本地服务，并用 SDK 验证“先返回 task ID，后台继续运行”；
6. 解释 `async_tasks` 独立状态通道为什么比只把 task ID 放在消息历史里更可靠；
7. 处理 worker 槽位、过时状态、完整 task ID、取消延迟、graph_id 不匹配和 ASGI/HTTP 传输等常见问题；
8. 完成一个小型后台研究编排，并把“运行成功”和“内容正确”分开验收。

## 二、和既往学习的衔接

| 已有能力 | 在本章中的用途 | 本章新增点 |
| --- | --- | --- |
| task02：模型、工具、环境变量 | 为 supervisor / researcher 提供模型和配置 | 不再把一次调用等同于一次完整任务 |
| task03：上下文和 Backend | 理解为什么任务元数据不能只依赖消息历史 | `async_tasks` 是专门的状态通道 |
| task04：规划、中间件、Checkpointer | 观察后台任务状态和主 Agent 状态边界 | 主 Agent 不等待，任务有自己的生命周期 |
| task05：同步子 Agent、Context Quarantine、CompiledSubAgent | 对比 `task` 和 `start_async_task` | Agent Protocol、thread/run、update/cancel |

本章暂时不重新讲工具调用、文件系统、普通子 Agent 定义和 CompiledSubAgent；只有在它们和异步生命周期发生边界冲突时再复习。

## 三、核心心智模型

### 1. 异步子 Agent 不是“给函数加 async”

Python 的 `async def` 解决的是协程如何被事件循环调度；`AsyncSubAgent` 解决的是一个独立 Agent 服务上的后台任务如何被启动和管理。

本章真正学习的是：

```text
主 Agent
  ├─ 启动后台任务，立即拿到完整 task_id
  ├─ 把控制权交还用户
  ├─ 用户问进度 → check_async_task
  ├─ 用户加约束 → update_async_task
  ├─ 用户要求停止 → cancel_async_task
  └─ 用户要总览 → list_async_tasks
```

### 2. 同步和异步的选择

| 判断维度 | 同步子 Agent | 异步子 Agent |
| --- | --- | --- |
| 任务时长 | 短任务，需要马上拿结果 | 可能持续数分钟或更久 |
| 主 Agent | 调用期间等待 | 启动后继续和用户交互 |
| 中途调整 | 没有自然入口 | 可以 update |
| 停止 | 不支持统一取消 | 可以 cancel |
| 状态 | 一次调用一次结果 | 独立 thread 持续累积会话 |
| 典型场景 | 一问一答、快速核验 | 长程研究、迁移、批量处理、持续编码 |

课程给出的经验法则是：大约 5 秒内能完成且需要立即拿结果，用同步；可能跑几分钟并且需要交互管理，用异步。这个阈值是启发式，不是框架硬限制。

### 3. AsyncSubAgent 配置契约

```python
from deepagents import AsyncSubAgent, create_deep_agent

async_subagents = [
    AsyncSubAgent(
        name="researcher",
        description="需要多次搜索和综合资料的长程研究",
        graph_id="researcher",
        # 不写 url：同部署 ASGI
        # url="https://research.example.com"：远程 HTTP
        # headers={"Authorization": "Bearer ..."}：自托管鉴权
    )
]

agent = create_deep_agent(model=model, subagents=async_subagents)
```

字段边界：

- `name`：唯一标识，主 Agent 启动任务时使用；
- `description`：模型的路由线索，要写清什么时候使用、擅长什么；
- `graph_id`：Agent Protocol 服务上的 graph / assistant ID；本地服务中必须和 `langgraph.json` 的 graph 键一致；
- `url`：省略时走同部署 ASGI，填写时走远程 HTTP；
- `headers`：远程自托管服务需要额外鉴权头时使用。

### 4. 五个“遥控器”

| 工具 | 作用 | 教学时必须观察的现象 |
| --- | --- | --- |
| `start_async_task` | 启动后台任务 | 很快返回完整 task ID，不等待 8 秒的 researcher |
| `check_async_task` | 查询实时状态与完成结果 | `running` 或终态；完成时取回最终输出 |
| `update_async_task` | 给已有任务追加指令 | task ID 不变；在同一 thread 上带历史重新运行 |
| `cancel_async_task` | 请求停止运行 | 工具先记录 `cancelled`；之后 check 仍可能读到服务端原始 `interrupted` |
| `list_async_tasks` | 列出全部跟踪任务 | 终态从缓存返回，非终态向服务端获取实时状态 |

典型生命周期：

```text
start → task_id
          ↓
          用户继续聊天
          ├─ check → running / success / error
          ├─ update → 同一个 task_id，追加新指令
          ├─ cancel → 工具确认 `cancelled`
          └─ list → 所有任务的当前总览
```

### 5. `cancelled` 和 `interrupted` 为什么可能同时出现

这里不能把所有状态都当成同一个字段。至少要区分三个观察面：

| 观察面 | 典型状态 | 含义 |
| --- | --- | --- |
| `cancel_async_task` 的工具结果 / supervisor 缓存 | `cancelled` | 取消请求已被工具接受，并把任务记录标记为取消 |
| Agent Protocol 服务端的某次 `run.status` | `running`、`success`、`error`、`cancelled`、`interrupted` | 这一具体运行过程的状态 |
| LangSmith tracing | 可能显示 `interrupted` | 这条被观测的执行被中断，不等价于业务层“取消按钮”的文字确认 |

当前本地 `deepagents==0.7.19` 的实现中，`cancel_async_task` 会把 supervisor 的 `async_tasks` 写成 `cancelled`；但 `check_async_task` 会再次读取服务端 run，并用服务端返回的原始状态更新记录。因此，取消工具返回 `cancelled`，随后 check 或 tracing 最终显示 `interrupted`，并不矛盾。`update_async_task` 本身也会用 `multitask_strategy="interrupt"` 中断旧 run，再在同一个 thread 上启动新 run。

学习和排障时应记录完整的 `task_id/thread_id/run_id`，再判断状态来自哪一层；不能只看某条旧 ToolMessage，也不能把 tracing 的状态直接当成五个控制工具的返回值。

### 6. 为什么有 `async_tasks` 通道

消息历史可能被总结、裁剪或卸载。如果 task ID 只存在某条 `ToolMessage`，主 Agent 可能在上下文压缩后失去对后台任务的引用。

Deep Agents 将任务元数据独立保存到 `async_tasks` state channel，典型字段包括 task ID、子 Agent 名、thread ID、run ID、状态和时间戳。这样消息历史可以压缩，任务仍然可以通过 `list_async_tasks` 找回。

这与 task03 的文件系统、task04 的 `todos` 是同一类设计思想：

```text
会被截断的对话细节 → messages / Backend
必须持续可引用的任务状态 → async_tasks
```

## 四、传输方式与部署拓扑

### 1. ASGI 与 HTTP

| 方式 | 配置 | 特点 | 适合 |
| --- | --- | --- | --- |
| ASGI | 不写 `url` | 同一个服务内调用，零网络鉴权配置 | 本地起步、绝大多数同部署场景 |
| HTTP | 填 `url`，必要时填 `headers` | 远程 Agent Protocol 服务，可独立扩缩容 | 不同团队、不同资源画像、独立发布 |

当前学习顺序固定为：先单部署 + ASGI，再理解拆分部署 + HTTP，最后只认识混合拓扑，不急着做远程部署。

### 2. 三种拓扑

```text
Single：  supervisor + researcher ── ASGI ── 同一个 Agent Server

Split：   supervisor ── HTTP ── researcher 的独立 Agent Server

Hybrid：  一部分子 Agent 走 ASGI，特殊资源型子 Agent 走 HTTP
```

### 3. 一个容易忽略的本地版本边界

课程叙述以 `deepagents>=0.5.0` 的预览特性为背景；当前 task05 锁定的本地环境是 `deepagents==0.7.19`、`langgraph==1.2.12`、`langgraph-sdk==0.4.5`。

我会以当前本地 API 为准。当前 `AsyncSubAgent` 类型说明特别提醒：省略 `url` 的本地 ASGI 传输需要异步父入口，例如 `ainvoke`；同步 `invoke` 需要一个带 `url` 的可访问 Agent Protocol 服务。这个差异是本章实验排障时的优先检查项。

## 五、本章的琐碎但关键的工程知识

### 服务启动

`langgraph.json` 至少声明依赖和 graph：

```json
{
  "dependencies": ["./"],
  "graphs": {
    "supervisor": "./graphs/supervisor.py:graph",
    "researcher": "./graphs/researcher.py:graph"
  },
  "env": "./.env"
}
```

然后从 `learning/task06` 启动：

```bash
uv run langgraph dev --n-jobs-per-worker 4
```

本地 Agent Server 需要 LangSmith 鉴权；模型还需要自己的提供商 Key。不要把真实 `.env` 提交到 Git。

### Worker 槽位

一个活跃 run 会占用一个 worker 槽位。一个 supervisor 同时管理 3 个后台任务时，至少要有 4 个槽位（1 个主任务 + 3 个子任务）。槽位不够可能表现为：

- `start_async_task` 长时间拿不到 task ID；
- 获得 task ID 但任务长期没有实质进展；
- 多个任务看似启动，实际排队。

先用 `--n-jobs-per-worker 4` 验证单任务，再按实验并发量调整。

### 状态必须实时查询

不能把历史中的“running”当作当前状态。回答进度前先调用 `check_async_task` 或 `list_async_tasks`。`success`、`error`、`cancelled` 是生命周期结果，不是业务质量结论；`interrupted` 则应先确认它来自具体 run 还是 tracing。

### ID 与追踪

不要截断 task ID。排障时保留：

```text
task_id ≈ thread_id
run_id   = 某次具体运行
```

LangSmith 中主 Agent 的 launch/check/update/cancel/list 工具调用和子 Agent 的 run 是不同 trace，thread ID 能把它们串起来。

### 取消不是瞬时魔法

`cancel_async_task` 发起取消请求后，至少要分别观察：取消工具的确认、服务端具体 run 的状态、LangSmith tracing 中该 run 的结束状态。取消后再次 `check_async_task` 或 `list_async_tasks`，确认你正在观察的究竟是哪一层；不要只相信旧的工具消息，也不要预设 tracing 必然显示 `cancelled`。

### 描述词会影响路由

好的描述：

```text
深度网络调研，需要多次搜索和信息综合时使用
```

坏的描述：

```text
帮你处理事情
```

`description` 是主 Agent 选择异步角色的重要线索，不是装饰性注释。

## 六、不要混淆的四组概念

1. **同步 SubAgent vs 异步 SubAgent**：前者是阻塞式一次委派，后者是服务支持的后台生命周期。
2. **异步 SubAgent vs Python asyncio**：前者是 Agent Protocol 的任务管理语义，后者是本地程序的协程调度机制。
3. **异步后台任务 vs 动态子 Agent**：异步重点是持续运行、查询、更新、取消；动态子 Agent 重点是由代码批量拆分、并发、汇总。后者属于后续章节，不在本章实现。
4. **任务成功 vs 内容正确**：run 进入 `success` 只表示执行结束；来源是否可靠、结论是否被证据支持需要单独验收。

## 七、推荐学习计划

建议分 6 次完成，每次 30～90 分钟。不要一次把所有 API 背下来；每次只完成一个可观察的行为，并在下一次开始前先回忆上一节。

### Session 0：定位本章新增内容（20～30 分钟）

目标：把 task05 的同步委派和 task06 的后台生命周期分开。

动作：

1. 阅读 [第一课](lessons/0001-async-lifecycle.html)；
2. 打开 [速查页](reference/async-subagents-reference.html)，遮住表格右侧；
3. 不看资料回答：同步委派为什么会阻塞？异步任务为什么需要 task ID？

产出：写下 3 句话，至少包含“阻塞”“task ID”“实时状态”。

### Session 1：先只验证 start 和 check（45～60 分钟）

目标：亲眼看到“主 Agent 先返回，researcher 后完成”。

动作：

1. 配置 `.env`，运行 `uv sync`；
2. 启动 `uv run langgraph dev --n-jobs-per-worker 4`；
3. 运行 `uv run python run_demo.py`；
4. 观察第一次响应是否很快返回 task ID；
5. 在 8 秒内查询一次，记录是否为 `running`；
6. 8 秒后再次查询，记录是否出现 `success` 和最终结果。

验收：不能只看最后文本，必须在记录中写出“启动耗时感受、task ID、至少两个状态”。

### Session 2：理解 update 的语义（45～60 分钟）

目标：确认追加指令不是“启动第二个任务”。

动作：

1. 启动任务后追加“完成时用 3 条 bullet”；
2. 记录 update 前后的 task ID 是否相同；
3. 对比 researcher 最终输出里是否出现最新指令；
4. 用自己的话解释“同一 thread + 新 run + 保留历史”的含义。

验收：能够区分“update 原任务”和“重新 start 新任务”，并说明为什么重新启动会丢失原任务的生命周期连续性。

### Session 3：练习 cancel、list 和状态边界（45～60 分钟）

目标：理解取消、总览和最终状态不是同一个动作。

动作：

1. 同时启动 2 个后台任务；
2. 用 `list_async_tasks` 查看总览；
3. 取消其中一个任务；
4. 立即和稍后各 check 一次，观察取消状态是否有延迟；
5. 检查另一个任务是否仍可独立完成。

验收：画一张状态图，至少包含 `running → success`、`running → cancelled` 和“具体 run / tracing 可能显示 `interrupted`”，并在旁边写“状态终态 ≠ 内容质量”。

### Session 4：ASGI、HTTP 与部署排障（60～90 分钟）

目标：不靠猜测定位配置错误。

动作：

1. 故意把 `graph_id` 改成未注册名称，记录错误现象并恢复；
2. 故意将 worker 槽位改小，观察任务排队现象，再恢复；
3. 对照 `url` 缺省/填写的两种配置，说明 ASGI 与 HTTP 的边界；
4. 阅读当前本地 `AsyncSubAgent` 类型说明，确认为什么本地 ASGI 要用异步入口；
5. 在 LangSmith 中用 thread ID 对照 supervisor 和 researcher trace。

验收：完成一张“现象 → 优先检查 → 修复”表，至少覆盖 graph_id、worker、旧状态、取消延迟四类问题。

### Session 5：小型后台研究编排（60～90 分钟）

目标：把异步机制连接回 task05 的研究和核验能力。

建议任务：让 `researcher` 后台整理“DeepAgents 中同步/异步子 Agent 的差异”，主 Agent 在后台任务运行时处理一个无关的小问题；之后查询最终报告，并明确区分：

```text
任务已完成
    ≠
报告内容已被证据支持
```

验收标准：

- 主 Agent 没有在启动后主动轮询到任务完成；
- 用户可以在后台运行期间继续提问；
- update 后仍然使用同一个 task ID；
- final report 保留来源或证据字段；
- 对报告做一次人工或 Pydantic 结构化验收。

### Session 6：间隔复习与口头答辩（30～45 分钟）

不看文件，回答以下问题：

1. 什么时候用同步 `task`，什么时候用 `AsyncSubAgent`？
2. `graph_id`、`thread_id`、`run_id` 各自是什么？
3. 为什么 `start_async_task` 后不应该立刻循环 `check_async_task`？
4. `async_tasks` 通道解决了什么问题？
5. `url` 缺省和填写分别意味着什么？
6. worker 槽位不足时，为什么会出现“有 task ID 但没有进展”？
7. 如何证明任务运行结束？如何另外证明结果正确？

如果有两道以上回答不稳，回到对应 Session 重做一次最小实验，而不是继续增加代码。

## 八、间隔复习安排

- 每次实验结束后：用 3 分钟默写五个控制工具；
- 下一次 session 开始前：不看资料解释上次实验的状态变化；
- Session 3 结束后：重新比较同步和异步；
- Session 6 结束后：隔一天重新运行一次 `list_async_tasks` / check 实验并复述排障顺序。

## 九、实验记录

### 环境与运行

- [ ] `uv sync` 成功
- [ ] `.env` 未提交真实密钥
- [ ] `langgraph dev` 成功启动
- [ ] `supervisor` 与 `researcher` 都在 `langgraph.json` 注册
- [ ] worker 槽位至少能容纳 1 个主任务 + 1 个子任务

### 生命周期

- [ ] `start_async_task` 很快返回完整 task ID
- [ ] 看到过 `running`
- [ ] 看到过 `success`
- [ ] `update_async_task` 后 task ID 未改变
- [ ] `cancel_async_task` 后分别记录工具结果、check/list 结果和 tracing 状态
- [ ] 能解释 `cancelled` 与 `interrupted` 可能来自不同观察层
- [ ] `list_async_tasks` 能列出多个任务

### 理解与验收

- [ ] 能解释 async subagent 不是普通 Python 协程
- [ ] 能解释 ASGI 与 HTTP 的选择
- [ ] 能解释 `async_tasks` 为什么独立于 messages
- [ ] 能区分任务生命周期成功和研究内容正确
- [ ] 能使用 thread/task/run ID 做一次 trace 对照

## 十、资料

### 主要资料

- [LangChain 官方：Async subagents](https://docs.langchain.com/oss/python/deepagents/async-subagents)：当前 API 的配置、五个控制工具和生命周期。
- [LangChain 官方文档源码：async-subagents.mdx](https://github.com/langchain-ai/docs/blob/main/src/oss/deepagents/async-subagents.mdx)：用于核对文档实现与示例。
- [Datawhale 第 6 章源码](https://github.com/datawhalechina/deepagents-in-action/blob/main/content/ch06-async-subagents.md)：本课程的章节叙事、本地 ASGI 示例、排障清单和学习顺序。
- [LangChain：Agent Protocol](https://blog.langchain.dev/agent-protocol-interoperability-for-llm-agents/)：理解 thread、run 和标准 Agent 服务接口为什么适合承载后台任务。

### 参考实现

课程提到的 `async-deep-agents` 完整示例适合在本章最小实验通过后再阅读；先理解本地脚手架，再看远程部署，避免把网络、鉴权、模型和异步生命周期一次混在一起。

## 十一、当前状态

本目录已经建立本章的学习计划、最小 ASGI 实验脚手架、速查页和第一课。Session 0 的概念回忆已经完成；正式学习记录见 `learning-records/0001-async-lifecycle-basics.md`。完成实验并能解释状态变化后，再追加后续记录。

