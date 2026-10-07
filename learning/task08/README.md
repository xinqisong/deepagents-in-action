# Task 08：课程资料简报审核 Agent

这里的“Agent C”指 [Task 01 的 AgentSeek `deepagents/research` 模板](../task01/README.md)。清单覆盖此前实际学习的 Task 01–07（课程第 1–9 章）；第 10 章及以后尚未纳入。**模板原有能力**和**后续章节可添加的能力**分开标明，避免误以为下面所有功能都已装在 Task 01 项目中。

用户已选定“课程资料简报审核”作为综合 demo。清单汇总课程覆盖与已有实验，不代表每项都已独立实测；具体实践状态以各 Task 的学习记录为准。

## 已选场景与验收

**核心能力**：同步子 Agent 委派与上下文隔离（A14、A15），工具调用前人工审批及恢复（A32、A35）。自定义资料工具（A04）和 Checkpointer（A27）支撑流程。

```text
用户请求 → 主 Agent 调用 task(research-agent)
         → researcher 列出并读取两份本地资料，返回带来源的发现
         → 主 Agent 生成简报，调用 publish_brief
         → 审批暂停（此时没有发布文件）
         → approve：生成一个本地 Markdown 文件
           reject：不生成发布文件
```

这个结构沿用 Task 01 模板的“主 Agent 协调、research-agent 查证、主 Agent 汇总”分工。Task 01 的 Tavily 搜索在本演示中换为两份固定课程资料，方便重复核对同一组证据；新增的 `publish_brief` 是受人工审批保护的模拟发布工具。`langgraph.json` 保留模板式图入口，演示交互使用命令行。

### 运行

在 `learning/task08` 目录执行：

```bash
uv sync
uv run python verify_offline.py
uv run python demo.py --offline
```

离线检查和 `--offline` 交互演示使用脚本化模型，不需要 API Key。它们在真实 DeepAgents 图中走过同步委派、资料工具调用、发布审批暂停、批准与拒绝恢复。检查脚本预期看到两个 `PASS`；它还核对审批前零文件、子 Agent 内部工具消息未进入主 Agent 消息、批准后恰好一份以及同内容重复发布不新增文件。脚本化模型验证调用链和状态边界，不验证真实模型是否会自主选择正确工具。

真实模型的交互演示：

```bash
cp .env.example .env
# 填入 OPENAI_API_KEY；使用兼容服务时还要填写 OPENAI_API_BASE 和 AGENTSEEK_MODEL
uv run python demo.py
```

CLI 会显示研究员结果、待审批简报和审批前的文件数。输入 `approve` 后，检查 `published/<thread_id>/brief-<hash>.md`；输入 `reject` 或直接回车，该次运行的发布目录仍为空。每次运行使用新的 `thread_id`，本演示的 `InMemorySaver` 只支持同一进程内恢复。图服务入口可通过 `uv run langgraph dev` 启动，但命令行脚本是本场景的直接验收入口。

### 主要文件

| 路径 | 作用 |
| --- | --- |
| `src/course_brief_agent/agent.py` | 主 Agent、同步 researcher、发布审批和 Checkpointer |
| `src/course_brief_agent/tools.py` | 本地资料读取和模拟发布工具 |
| `src/course_brief_agent/model.py` | 沿用 Task 01 的模型变量名，接入 OpenAI-compatible 模型 |
| `data/` | 固定课程资料 |
| `demo.py` | 真实模型的人工批准或拒绝入口 |
| `src/course_brief_agent/offline_model.py` | 固定工具调用顺序，供离线交互和检查使用 |
| `verify_offline.py` | 不依赖模型服务的端到端边界检查 |

模拟发布只写本地 Markdown。报告内容仍需人工审阅；审批通过表明工具获准执行，不代表研究结论已被自动核实。相关 API 边界见 [Deep Agents Subagents](https://docs.langchain.com/oss/python/deepagents/subagents) 与 [Human-in-the-loop](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop)。

## 此前课程能力清单

## 1. 模板基础与工具调用

| 编号 | 能力 | 来自 | 能观察到什么 |
| --- | --- | --- | --- |
| A01 | AgentSeek 模板与生命周期 | Task 01，模板原有 | 生成项目、安装依赖、启动后端和前端，查看图入口 |
| A02 | 模型接入与切换 | Task 01–02，模板原有或配置扩展 | 用模型提供商、模型名和密钥配置 `create_deep_agent` |
| A03 | 对话与工具调用循环 | Task 02，基础能力 | 模型请求工具、工具执行、模型根据结果继续回答 |
| A04 | 自定义工具 | Task 02，扩展能力 | 用函数参数、类型和说明定义领域操作 |
| A05 | 网络研究与来源收集 | Task 01–02，模板原有 | Tavily 搜索、抓取网页、用 `think_tool` 检查研究缺口并汇总引用 |
| A06 | 运行观察与追踪 | Task 01–02，模板与 LangSmith | 在前端或 Trace 查看消息、工具调用、耗时和执行路径 |

## 2. 上下文、文件与规划

| 编号 | 能力 | 来自 | 能观察到什么 |
| --- | --- | --- | --- |
| A07 | 虚拟文件工具 | Task 03，DeepAgents 能力 | 列目录、读写和编辑文件、按关键词查找资料 |
| A08 | 大结果卸载到文件 | Task 03，上下文管理 | 大型工具结果离开消息窗口，后续再按需读取 |
| A09 | 对话历史压缩 | Task 03–04，中间件能力 | 长对话被总结，保留继续任务所需的上下文 |
| A10 | 可插拔文件后端 | Task 03，DeepAgents 能力 | 选择临时 State、磁盘 Filesystem、长期 Store 或路径路由 Composite；课程还介绍 LocalShell 与沙箱后端 |
| A11 | 文件路径隔离与权限 | Task 03、第 7/9 章扩展 | 限制可读写路径，对敏感写入拒绝或要求审批 |
| A12 | 任务规划与进度 | Task 04，显式配置中间件 | `write_todos` 创建、更新待办与完成状态 |
| A13 | 中间件扩展 | Task 04，第 9 章深化 | 在模型或工具调用前后加入规划、压缩、检查等处理 |

## 3. 同步与异步多 Agent

| 编号 | 能力 | 来自 | 能观察到什么 |
| --- | --- | --- | --- |
| A14 | 同步子 Agent 委派 | Task 01、05，模板已有研究员 | 主 Agent 调用 `task`，等待 researcher 返回结果后继续 |
| A15 | 子 Agent 上下文隔离 | Task 05 | 子 Agent 的搜索和中间消息不全部进入主 Agent 对话 |
| A16 | 专家分工与工具隔离 | Task 05 | 不同子 Agent 有独立说明、工具集和模型配置 |
| A17 | 通用子 Agent 配置 | Task 05 | 使用、覆盖或禁用 general-purpose 子 Agent |
| A18 | 编译图作为子 Agent | Task 05 | 将已有 LangGraph 工作流包装成 `CompiledSubAgent` |
| A19 | 多子 Agent 协作 | Task 05 | 按专业分工顺序或并行委派，再由主 Agent 汇总 |
| A20 | 子 Agent 结构化结果 | Task 05 | 按 JSON 等约定返回摘要、来源和置信信息 |
| A21 | 异步子 Agent 启动 | Task 06，第 6 章扩展 | `start_async_task` 立即返回任务 ID，后台继续执行 |
| A22 | 异步任务控制 | Task 06，第 6 章扩展 | `check`、`update`、`cancel`、`list` 管理后台任务生命周期 |
| A23 | 异步服务与并发编排 | Task 06，第 6 章扩展 | Agent Protocol 上的 thread/run、ASGI 或 HTTP 传输、worker 并发和状态追踪 |

## 4. 可复用 Skill 包

这里的 **Skill** 特指课程第 7 章的 `SKILL.md` 工作流包，和你说的“Agent 能力”不是同一个概念。它仍是此前学过的一类可选能力，不预设放进综合 demo。

| 编号 | 能力 | 来自 | 能观察到什么 |
| --- | --- | --- | --- |
| A24 | Skill 渐进加载 | Task 06，第 7 章扩展 | 先读取名称和描述，任务匹配时再读取 `SKILL.md` 正文 |
| A25 | Skill 资源组织与多来源加载 | Task 06，第 7 章扩展 | 按需读取 references、assets、scripts；从文件、State 或 Store 加载 |
| A26 | Skill 作用域与权限 | Task 06，第 7 章扩展 | 区分共享与个人 namespace，并限制读取、写入或执行 |

## 5. 短期状态与长期记忆

| 编号 | 能力 | 来自 | 能观察到什么 |
| --- | --- | --- | --- |
| A27 | 同线程短期状态 | Task 07，第 8 章扩展 | Checkpointer 在同一 `thread_id` 内保存对话和待恢复状态 |
| A28 | 跨线程长期数据 | Task 07，第 8 章扩展 | Store 在新线程中仍可读到已保存的资料或偏好 |
| A29 | 路径路由的混合存储 | Task 07，第 8 章扩展 | `CompositeBackend` 将临时文件与持久化记忆路由到不同后端 |
| A30 | 记忆作用域与隔离 | Task 07，第 8 章扩展 | 按用户、组织或 Agent 的 namespace 控制读取与写入 |
| A31 | 记忆写入边界与并发 | Task 07，第 8 章扩展 | 检查写入证据、冲突和审批条件，避免把“说已记住”当作成功 |

## 6. Human-in-the-Loop 与安全执行

| 编号 | 能力 | 来自 | 能观察到什么 |
| --- | --- | --- | --- |
| A32 | 工具调用前暂停 | Task 07，第 9 章扩展 | `interrupt_on` 在敏感工具执行前生成待审批请求 |
| A33 | 四类人工决定 | Task 07，第 9 章扩展 | `approve`、`reject`、`edit`、`respond` 分别改变恢复路径 |
| A34 | 条件审批 | Task 07，第 9 章扩展 | 按工具参数判断风险，只拦截满足条件的调用 |
| A35 | 审批恢复与状态核对 | Task 07，第 9 章扩展 | 用同一 thread 和 Checkpointer 恢复，并核对工具是否真的执行 |
| A36 | 同批与并行审批 | Task 07，第 9 章扩展 | 同批 action 按顺序决策；并行中断按各自 ID 恢复 |
| A37 | 子 Agent 内审批 | Task 07，第 9 章扩展 | 敏感工具由子 Agent 持有，审批发生在子 Agent 的调用处 |
| A38 | 文件权限触发审批 | Task 06–07，权限与审批结合 | 敏感路径写入时由权限规则暂停或拒绝 |
| A39 | 中断重放与幂等副作用 | Task 07，第 9 章扩展 | 恢复可能重跑节点；用幂等操作避免重复写入或发布 |
| A40 | 自定义中断与验证 | Task 07，第 9 章课程范围 | 在中间件或图节点中验证输入、设置人工断点或调试暂停 |

能力清单保留为后续扩展参考；本次已选的核心能力和验收现象见文档开头。
