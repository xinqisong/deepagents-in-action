# Task 05 学习记录：子 Agent 与上下文隔离

本次学习对应第 5 章“子 Agent 与上下文隔离——让 Agent 学会委派”。

课程原文：

<https://datawhalechina.github.io/deepagents-in-action/chapters/ch05-subagents/>

## 一、本章要解决的问题

主 Agent 如果亲自完成一个需要多次搜索、读取和整理的子任务，所有中间工具调用都会进入它的上下文。上下文越长，主 Agent 越难保持任务主线，也会增加模型输入成本。

子 Agent 的核心不是“多一个模型”，而是把一段复杂工作放进独立上下文中执行，主 Agent 最后只接收结果摘要。这种设计在本章称为 Context Quarantine（上下文隔离）。

## 二、第一步：最小委派实验

当前 `agent.py` 只包含：

- 一个主 Agent，负责协调；
- 一个名为 `researcher` 的子 Agent，负责搜索资料并总结；
- 一个 `internet_search` 工具，只给 `researcher` 使用；
- 一次明确要求主 Agent 委派的调用。

先运行：

```bash
cd learning/task05
uv run python agent.py
```

重点观察：

1. 主 Agent 是否发起了 `task` 工具调用；
2. `task` 调用的子 Agent 名称是否为 `researcher`；
3. `internet_search` 是否由子 Agent 调用；
4. 主 Agent 最终拿到的是摘要，而不是子 Agent 的每一步内部过程。

## 三、先用自己的话回答

运行前先猜，运行后再修正：

1. 为什么主 Agent 不应该亲自完成所有研究步骤？
2. `researcher` 的 `description` 对主 Agent 的路由有什么作用？
3. 如果子 Agent 返回了大量原始搜索结果，上下文隔离的收益还剩多少？

## 四、当前实验清单

- [x] 成功创建 `task05` 分支
- [x] 能解释 `task()` 是委派入口
- [x] 观察到 `researcher` 被调用
- [x] 观察到子 Agent 使用自己的工具
- [x] 能解释独立上下文与最终结果回传的关系
- [x] 能解释为什么返回结果要设置长度和格式边界

## 五、第一次运行的排查结论

如果运行结果显示子 Agent 搜索 `/`、`/home` 等路径，不要先认为上下文隔离失败。DeepAgents 默认会自动加入名为 `general-purpose` 的子 Agent；它拥有文件系统工具，可能会被模型优先选择。

本实验随后通过 `HarnessProfile` 关闭默认 `general-purpose`，让 `task` 工具只暴露 `researcher`。这不是生产项目中唯一的配置方式，但很适合用来验证“主 Agent 到底委派给了谁”。

判断委派对象时，要看 `AIMessage` 中 `task` 调用的参数 `subagent_type`，不能只看 `tool_calls=['task']`，因为后者只能说明调用了委派入口。

## 六、当前学习进度与遇到的问题

本章实验已经从最小委派推进到 CompiledSubAgent、多子 Agent 顺序协作和结构化 JSON 校验。当前流程为：

```text
主 Agent → compiled-url-router → fact_checker → 最终核验结果
```

已完成：

- [x] 创建并切换到 `task05` 分支；
- [x] 理解 `task()`、`name`、`description`、`system_prompt` 和 `tools`；
- [x] 理解 Context Quarantine 与最终结果回传；
- [x] 关闭不需要的默认 `general-purpose` 子 Agent；
- [x] 编写并编译 LangGraph URL 核验子图；
- [x] 将 `CompiledSubAgent` 接入 DeepAgents；
- [x] 实现 `researcher`、`compiled-url-router` 和 `fact_checker` 的职责分工；
- [x] 实现成功、无 URL、访问失败三条分支；
- [x] 使用 Pydantic 校验 `VerificationReport` JSON；
- [x] 验证主 Agent 将第一个子 Agent 的完整结果传给第二个子 Agent。

### 遇到的问题与解决方式

1. **误把 URL 路由器当成事实核验器**：将 URL 检查与语义事实判断拆分为 `compiled-url-router` 和 `fact_checker`。
2. **无 URL 时 `urls[0]` 越界**：先判断列表是否为空，再读取第一个 URL。
3. **`check_content` 未注册**：定义函数后还必须调用 `builder.add_node("check_content", check_content)`。
4. **`unescape` 未导入**：增加 `from html import unescape`。
5. **HTML/CSS 造成 `summary` 假阳性**：先移除 `script`、`style`、`noscript`，再提取正文并使用更有判别力的短语。
6. **子图状态不会自动传给父 Agent**：将 `route`、HTTP 状态、URL、关键词和证据片段写入最终 JSON。
7. **成功和失败分支格式不一致**：让 `content_checked`、`search_more`、`fetch_failed` 都使用 `VerificationReport`。
8. **主 Agent 重复调用路由器**：在协调者提示词中明确路由器只调用一次，之后交给 `fact_checker`。
9. **结构化输出与模型能力不兼容**：Thinking mode 不支持所需的强制 `tool_choice`，SiliconFlow 当前接口也不支持对应的原生 JSON Schema，因此暂时使用“提示词要求 JSON + Pydantic 校验”的降级方案。

### 当前结论边界

- URL 可访问不等于来源支持结论；
- 关键词命中不等于事实成立；
- `semantic_verification: not_performed` 只表示路由子图没有做语义判断；
- `fact_checker` 才负责根据证据片段进行语义核验；
- `final result` 不应自动改写成“最终摘要”；
- `context quarantine` 的术语归属、具体隔离实现和异步范围仍需谨慎表述。

## 七、下一步：异步子 Agent 与并行编排

当前 `researcher → fact_checker` 是有依赖的顺序流水线，不能并行。官方文档检索和源码检索互不依赖，可以采用：

```text
docs_researcher ─────┐
                     ├─ evidence_merger → fact_checker
source_code_reviewer ┘
```

下一节需要学习 Async Subagent 的后台运行、状态查询、追加指令、取消和恢复；它不只是同时调用两个普通子 Agent。

## 八、运行命令

```bash
cd learning/task05
uv run python agent.py
uv run python url_branch_demo.py
timeout 120s uv run python compiled_subagent_demo.py
```

不要提交真实的 `.env`、API Key 或其他私密配置。
