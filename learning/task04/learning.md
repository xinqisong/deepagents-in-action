# Task 04 学习记录：任务规划与中间件

本次学习对应第 4 章“任务规划与分解——让 Agent 学会拆解复杂任务”。

本次实操案例是“为 Agent 开发课程网站设计首页”。已经在前面掌握的虚拟文件系统和基础 Agent 结构不再重复，本轮重点观察：一个真实的网站设计任务如何被拆分、如何连续调用搜索工具，以及如何用验收标准检查设计方案。

课程原文：

<https://datawhalechina.github.io/deepagents-in-action/chapters/ch04-task-planning/>

## 一、学习目标

完成后，我应该能够：

1. 判断一个任务是否值得启用任务规划；
2. 解释 `TodoListMiddleware` 如何提供 `write_todos`、`todos` 和规划提示词；
3. 读懂 `pending`、`in_progress`、`completed` 的含义，并知道完成标记不是质量证明；
4. 区分任务清单、文件系统、对话总结和 Checkpointer 的职责；
5. 区分 Node-style Hook 与 Wrap-style Hook 的适用场景；
6. 解释 `PatchToolCallsMiddleware`、Retry 和 Checkpointer 为什么不能互相替代；
7. 使用一个受限工作区完成“规划—执行—写文件—复查”的最小实验。

## 二、先建立一个核心心智模型

复杂 Agent 任务可以拆成四个互补的状态面：

```text
目标与步骤       → todos：接下来要做什么、当前做到哪一步
资料与中间产物   → Backend：已经得到什么、以后从哪里取回
当前模型输入     → messages：这一轮真正需要理解的内容
跨次运行恢复     → Checkpointer：下一次 invoke 如何接着上次状态继续
```

这四者不是同一个东西：

- `todos` 不是消息历史，也不是最终结果；
- Backend 中有文件，不代表 Agent 已经读取并理解它；
- 对话被总结后，`todos` 可以继续保留，但细节是否可回查取决于 Backend；
- Checkpointer 负责状态恢复，不负责验证报告是否正确。

## 三、章节知识总结

### 1. 什么时候需要规划

单步问答或短工具调用中，计划可能比任务本身还长，可以关闭。搜索、比较、写作、测试等多个阶段组成的长程任务，容易漏步骤或失去主线，适合启用并观察真实完成率、轨迹长度和最终产物。

规划带来的收益是“显式的工作记忆”：Agent 能先拆分目标，再按步骤推进，并在发现新信息时调整计划。但 `write_todos` 存在，不代表模型一定会合理调用；是否有效必须通过任务轨迹和结果验证。

### 2. `TodoListMiddleware` 提供什么

在 v0.7 中，任务规划是按需启用的：

```python
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_deep_agent(
    model=model,
    middleware=[TodoListMiddleware()],
)
```

启用后主要获得：

1. `write_todos` 工具：创建和更新任务清单；
2. `todos` 状态：让 Agent 和 UI 能看到进度；
3. 规划指导提示词：提醒 Agent 先规划、再逐步执行。

### 3. Todo 的数据结构与状态

```python
{
    "content": "读取资料并整理核心概念",
    "status": "pending",
}
```

状态含义：

| 状态 | 含义 | 关键检查 |
| --- | --- | --- |
| `pending` | 已规划但未开始 | 步骤是否具体、可执行 |
| `in_progress` | 当前正在执行 | 是否真的发生了对应工具调用 |
| `completed` | Agent 标记完成 | 产物是否存在且质量合格 |

通常是 `pending → in_progress → completed`，但模型可以根据新信息调整清单。它不是框架强制执行的固定状态机。

### 4. 任务清单的持久化边界

任务清单存放在 Agent State 的 `todos` 字段，与消息历史分开。自动摘要压缩消息时，`todos` 不会因为消息被总结而自动删除。

但要在多次 `invoke()` 间继续运行，必须：

1. 配置 Checkpointer；
2. 复用同一个 `thread_id`；
3. 根据部署场景选择合适的持久化实现。

`InMemorySaver` 只保留当前进程状态；进程重启后要恢复，必须使用数据库等持久化 Checkpointer。子 Agent 也有自己的状态，显式声明的 `subagents` 不会自动读取主 Agent 的清单。

### 5. 中间件是 Agent 能力的装配层

Deep Agents 构建在 LangChain 之上，`create_deep_agent()` 的重要工作之一，就是把不同中间件装配到 Agent 上。可以按配置入口理解：

| 配置入口 | 例子 | 作用 |
| --- | --- | --- |
| 默认提供 | `FilesystemMiddleware`、`SummarizationMiddleware`、`PatchToolCallsMiddleware` | 文件工具、上下文压缩、补齐缺失工具响应 |
| 专用参数 | `skills=`、`memory=`、`interrupt_on=`、`subagents=` | 技能、记忆、人工审批、子 Agent |
| `middleware=[...]` | `TodoListMiddleware`、Retry、限制调用次数 | 按需加入或替换执行策略 |

同名实例被替换时，不会自动把新旧配置逐字段合并；替换后应重新验证权限、Backend 和子 Agent 配置。

### 6. Node-style 与 Wrap-style Hook

| Hook 风格 | 典型 Hook | 适合场景 |
| --- | --- | --- |
| Node-style | `before_agent`、`before_model`、`after_model`、`after_agent` | 校验、状态更新、审计、人工中断 |
| Wrap-style | `wrap_model_call`、`wrap_tool_call` | 重试、缓存、降级、请求/响应转换 |

对 `interrupt()` 来说，Node-style 有更清晰的图节点边界，暂停和恢复更容易推断；Wrap-style 位于模型或工具节点内部，恢复时可能连同 `handler` 一起重放。因此人工中断通常优先放在 Node-style Hook 中，带副作用的操作还要考虑幂等性。

### 7. 几个容易混淆的职责

| 问题 | 负责机制 | 不负责什么 |
| --- | --- | --- |
| 历史里有工具调用但没有工具响应 | `PatchToolCallsMiddleware` | 不重新执行工具、不证明外部操作已撤销 |
| 工具调用遇到可重试异常 | Retry 中间件 | 不自动判断业务结果是否正确 |
| 下次运行接着上次状态 | Checkpointer + 同一 `thread_id` | 不负责任务拆解或内容审核 |
| 报告、文件、引用是否可信 | 应用校验、评测或人工审核 | 不由 `completed` 标记自动保证 |

### 8. 规划与上下文总结如何协同

长任务中，工具结果可能很大，对话消息也会很多。Deep Agents 可以把大结果卸载到 Backend，并在上下文接近阈值时总结旧消息。模型本轮看到的是摘要与近期消息，而 `todos` 继续作为任务锚点保存步骤进度。

这形成一条实用链路：

```text
write_todos 制定步骤
        ↓
执行工具并把资料/中间结果写入 Backend
        ↓
上下文过长时总结消息，但保留任务清单
        ↓
按 todos 找到下一步，再用 read_file / grep 取回细节
        ↓
检查真实产物，而不是只看 completed
```

### 9. 手动组合规划与文件系统

如果使用较底层的 LangChain `create_agent()`，可以显式组合：

```python
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from deepagents.middleware import FilesystemMiddleware

agent = create_agent(
    model=model,
    tools=[],
    middleware=[
        TodoListMiddleware(),
        FilesystemMiddleware(),
    ],
)
```

在更完整的配置中，文件工具和摘要中间件应共享同一个 Backend，确保摘要中保存的历史路径之后仍能通过文件工具读取。手动创建摘要中间件时，要显式设置 `trigger` 和 `keep`；看到某个节点存在，不等于摘要已经触发。

## 四、推荐学习路线

### 第 1 步：先用一句话解释规划

尝试回答：

```text
为什么一个“能调用工具”的 Agent，仍然可能无法稳定完成一项复杂任务？
```

参考方向：工具调用解决“能做某个动作”，任务规划解决“是否按完整顺序推进一组动作”。

### 第 2 步：跑通最小实验

```bash
cd learning/task04
cp .env.example .env
# 编辑 .env
uv sync
uv run python agent.py
```

观察四件事：

1. 是否真的调用了 `write_todos`；
2. `todos` 是否出现 `pending → in_progress → completed`；
3. 是否进行了多次 `internet_search`，并把搜索结果用于网站方案；
4. Agent 是否在最终回答中把“完成标记”和“设计结论仍需人工判断”区分开。

### 第 3 步：做一次故意失败的验证

把任务提示中的输出路径改成一个新文件名，再观察 Agent 是否真的创建文件。然后把“完成”要求保留，但去掉复查步骤，比较最终回答是否更容易只报告状态而忽略内容质量。

### 第 4 步：比较是否启用 Todo

准备两个配置：

```python
# A：关闭 TodoListMiddleware
create_deep_agent(model=model, backend=backend)

# B：显式开启
create_deep_agent(
    model=model,
    backend=backend,
    middleware=[TodoListMiddleware()],
)
```

使用同一个多步任务，记录：工具调用次数、是否遗漏步骤、输出文件是否存在、最终内容是否完整。不要只凭一次运行得出结论。

### 第 5 步：画清职责边界

用自己的话完成以下判断：

- 工具响应缺失，但不应重跑工具：`PatchToolCallsMiddleware`；
- 工具异常且允许重试：Retry；
- 需要跨次运行恢复：Checkpointer；
- 报告内容是否正确：校验或人工审核。

## 五、实验记录

### 网站设计案例实验

- [ ] `TodoListMiddleware` 创建成功
- [ ] Agent 调用了 `write_todos`
- [ ] 观察到至少一次 `in_progress`
- [ ] Agent 调用了多次 `internet_search`
- [ ] 最终输出首页信息架构和设计 brief
- [ ] 最终回答区分了进度标记与设计质量判断

### 我的关键理解

```text
学会了任务规划与产物验收，验证了内存检查点的恢复边界，区分了消息修补与重试，理解了摘要保留重点及中间件配置替换。
```

### 已完成的互动实验

- 本地总结实验：观察到 write_todos 调用和总结文件生成，并手动对照资料确认内容合格。
- 网站设计案例：输出首页设计方案及验收清单，列出待业务方确认事项；最终报告声称动态新增了任务，但未通过工具调用记录核实新增时机。
- 同一 Checkpointer、同一 thread：第一个任务从 pending 变为 completed，消息数量从 4 增至 10。
- 同一 Checkpointer、不同 thread：新 thread 调用前状态为 {}，调用后没有原来的任务清单。
- 新 InMemorySaver、同名 thread：状态为 {}；原 Checkpointer 仍保留三个 pending 任务。该实验模拟更换内存存储，并非实际重启进程。

### 学习中修正的理解

- completed 只是状态标记，需要检查产物存在、内容完整且符合要求。
- 恢复状态需要原存档仍然存在；仅复用 thread_id 不够。
- PatchToolCallsMiddleware 补齐缺失响应，不重新执行工具；Retry 按策略重试，需考虑重复副作用。
- 摘要应保留目标、长期约束、关键决策、必要结论和未完成事项。
- 同名中间件完整实例替换；需要的 Backend、trigger、keep 等配置要显式保留。

### 遇到的问题与修复

| 问题 | 原因 | 修复方式 |
| --- | --- | --- |
| 待补充 | 待补充 | 待补充 |

## 六、和下一章的连接

第 4 章解决“复杂任务如何拆解和推进”，第 5 章将把其中一部分步骤委派给子 Agent。下一步要继续追问：主 Agent 的任务清单如何与子 Agent 的独立状态协作？哪些上下文应该隔离，哪些结果应该回传？
