# Task 03 学习记录：虚拟文件系统与上下文管理

## 一、学习目标

本次学习对应课程第 3 章：

<https://datawhalechina.github.io/deepagents-in-action/chapters/ch03-virtual-filesystem/>

完成后，我应该能够：

1. 解释为什么文件系统可以作为 Agent 的“外部上下文”。
2. 说清楚 `ls`、`read_file`、`write_file`、`edit_file`、`delete`、`glob`、`grep` 的职责和边界。
3. 用 `FilesystemBackend` 搭建一个受限的本地实验工作区。
4. 区分临时存储、本地磁盘、跨会话存储、混合路由和沙箱后端。
5. 理解大工具结果卸载、对话历史总结，以及它们对上下文窗口的影响。
6. 发现文件系统 Agent 的安全风险，并能提出最小防护方案。

## 二、先建立一个核心心智模型

传统 Agent 容易把资料、搜索结果和中间推理全部塞入 prompt，导致上下文不断膨胀。虚拟文件系统把这个流程拆成两层：

```text
模型上下文：当前要理解和决策的少量信息
       ↕ read / grep / glob
虚拟文件系统：资料、中间结果、草稿和历史记录
```

因此，文件系统的价值不是“多了几个工具”，而是让 Agent 能够：

- 按需读取，而不是一次性加载全部资料；
- 把中间结果结构化保存，避免每轮重新计算；
- 用搜索定位信息，再精读命中的文件；
- 在上下文接近上限时，将大结果和旧消息移出模型输入。

## 三、章节重点总结

### 1. 七个内置文件工具

| 工具 | 作用 | 学习时要注意 |
| --- | --- | --- |
| `ls` | 查看目录和文件元信息 | 先观察工作区，再决定读取什么 |
| `read_file` | 读取文件 | 支持 `offset` 和 `limit`，大文件要分片读取；可能返回下一段偏移量 |
| `write_file` | 新建或完整覆盖文件 | 同路径已有文件时会覆盖，不能把它当局部编辑使用 |
| `edit_file` | 精确替换已有内容 | 适合局部修改，先确认目标文本唯一性 |
| `delete` | 删除文件或目录 | 是有破坏性的操作，应纳入权限控制和审批策略 |
| `glob` | 按路径模式找文件 | 结果可能被截断，必要时缩小目录或匹配模式 |
| `grep` | 按字面量搜索文件内容 | 可输出路径、匹配内容或计数；默认匹配数量也有限制 |

v0.7 的兼容要点：`read_file`、`grep`、`glob` 的返回结果可能不完整，必须关注分页或 `truncated=True`；应用如果解析工具文本，不能假设旧版的空结果文本、行号分隔符和返回格式仍然不变。优先使用结构化 Backend 结果。

### 2. 上下文自动管理

当工具输入或输出超过 `tool_token_limit_before_evict`（默认 20,000 tokens）时，Deep Agents 会把完整结果写入虚拟文件系统，并在对话中保留文件路径和短预览。Agent 之后可以用 `read_file` 或 `grep` 取回原文。

当对话接近上下文阈值时，旧消息会保存到 Backend，模型本轮看到的是结构化摘要和近期消息。要区分两件事：

- 历史文件负责“以后还能查回细节”；
- 摘要负责“本轮减少模型输入”。

摘要是否可回查，取决于 Backend 是否成功保存以及文件是否仍可访问。

### 3. 后端决定文件存在哪里

| 后端 | 生命周期 | 适合场景 | 关键风险或限制 |
| --- | --- | --- | --- |
| `StateBackend` | 当前 thread 内 | 学习、临时草稿、默认配置 | 换 thread 后消失 |
| `FilesystemBackend` | 本地磁盘，永久修改 | 本地编程助手、CI | 可能读到敏感文件；必须限制 `root_dir` |
| `LocalShellBackend` | 本地磁盘 + Shell | 完全信任的个人开发环境 | 可执行任意 Shell，风险极高 |
| `StoreBackend` | 跨 thread 持久化 | 长期记忆、用户偏好 | 必须正确设计 `namespace` 做数据隔离 |
| `CompositeBackend` | 按路径混合路由 | 临时草稿 + 持久记忆 | 路由规则和权限边界要清晰 |
| 沙箱后端 | 隔离环境 | 不可信代码、生产执行 | 需要额外的沙箱服务和配置 |

本次基础实验使用 `FilesystemBackend(root_dir="...", virtual_mode=True)`。`virtual_mode=True` 很重要：仅设置 `root_dir` 并不等于已经阻止越界访问。

### 4. 权限与自定义策略

可以用 `FilesystemPermission` 按操作和路径声明 `allow`、`deny` 或 `interrupt`。规则采用 first-match-wins，所以更具体的规则必须放在宽泛规则之前。

如果声明式规则不够，可以包装或继承 Backend，统一拦截：

- `write` / `edit`：阻止敏感路径被修改；
- `delete`：不要遗漏删除能力；
- `read`：必要时屏蔽密钥和个人数据；
- `grep` / `glob`：避免搜索工具绕过读取限制；
- 审计日志、速率限制和内容检查。

## 四、推荐学习路线

### 第 1 步：先读懂“为什么需要文件系统”

阅读章节“为什么用文件系统管理上下文”和“内置文件系统工具”。不要急着背 API，先回答：

```text
如果所有搜索结果都留在 messages 中，会出现什么问题？
文件系统怎样把“保存”和“使用”拆开？
```

产出：用自己的话写一段 100～200 字的解释。

### 第 2 步：跑通最小文件操作实验

执行：

```bash
uv run python agent.py
```

观察 `workspace/` 的变化，并记录 Agent 是否实际调用了：

```text
ls → read_file → grep / glob → write_file → edit_file → read_file
```

产出：记录一条完整的“工具调用—文件变化—最终回答”链路。

### 第 3 步：专门练习读取与搜索

在 `workspace/` 中准备一份较长的 Markdown 文件，分别尝试：

- 用 `read_file` 的 `offset` / `limit` 分片读取；
- 用 `grep` 的 `files_with_matches` 快速定位文件；
- 用 `grep` 的 `content` 查看命中行；
- 用 `grep` 的 `count` 做统计；
- 用 `glob` 缩小搜索范围。

产出：写下“什么时候用 `glob`，什么时候用 `grep`，什么时候直接 `read_file`”的判断规则。

### 第 4 步：对比存储后端

建立三个小实验：

1. `StateBackend`：同一个 thread 中写入文件，再继续对话读取；换 thread 后验证文件是否消失。
2. `FilesystemBackend`：重启程序后读取本地文件，确认修改是持久的。
3. `CompositeBackend`：让 `/workspace/` 走临时存储，让 `/memories/` 走 `StoreBackend`，观察路径路由。

产出：完成一张“后端—生命周期—适用场景—风险”的对比表，不要只写“永久/临时”，要写清楚谁能访问、何时隔离。

### 第 5 步：验证上下文管理

不必一开始就构造超大真实数据，可以先理解并记录两个阈值：

- 大工具结果触发自动卸载的 `tool_token_limit_before_evict`；
- 模型上下文窗口触发摘要的阈值，默认按模型 profile 的 85% 估算。

然后设计一个大结果实验：让搜索或工具返回大量文本，确认对话里留下的是文件引用和预览，而完整结果进入 Backend。

产出：画出“工具结果 → 自动写文件 → 对话保留引用 → Agent 按需读取”的流程。

### 第 6 步：做一次安全审查

检查以下问题：

- `root_dir` 是否只指向专用实验目录？
- 是否显式开启 `virtual_mode=True`？
- 实验目录中是否可能出现 `.env`、私钥、云凭证？
- 是否真的需要 `LocalShellBackend`？
- 是否同时限制了写入、编辑和删除？
- `StoreBackend` 的 `namespace` 是否按用户或租户隔离？

产出：在本文件末尾写一段“我不会在生产环境直接复用的配置”，并说明原因。

### 第 7 步：用一个小项目收尾

让 Agent 维护一个“课程知识库”：

1. 把本章的若干概念写入多个 Markdown 文件；
2. 用 `glob` 找到所有笔记；
3. 用 `grep` 定位 `Backend`、`context`、`security`；
4. 读取命中的片段；
5. 写出 `workspace/ch03-summary.md`；
6. 用 `edit_file` 修正一个错误，再读取确认。

验收标准：总结文件存在、内容来自多个文件、至少发生过一次局部编辑，并且 Agent 没有越出实验根目录。

## 五、实验记录

### 基础实验

- [x] `FilesystemBackend` 创建成功
- [x] `virtual_mode=True` 已启用
- [x] Agent 成功列出工作区
- [x] Agent 成功读取 `lesson-source.md`
- [x] Agent 成功搜索关键词并写出总结
- [x] Agent 成功完成一次局部编辑

### 后端对比

- [x] `StateBackend`
- [x] `FilesystemBackend`
- [x] `StoreBackend`
- [x] `CompositeBackend`
- [x] 沙箱后端的适用边界

### 我的关键理解

```text
虚拟文件系统不是简单增加几个文件 API，而是把资料和中间结果放到当前模型上下文之外，
让 Agent 先按需保存、搜索和读取，再把当前真正需要的信息注入上下文。这样可以控制上下文规模，
也能让复杂任务拥有可复用的工作区。
```

### 遇到的问题与修复

| 问题 | 原因 | 修复方式 |
| --- | --- | --- |
| `UnsupportedProtocol: Request URL is missing an 'http://' or 'https://' protocol` | 模型请求阶段没有读取到有效的 Base URL；Shell 中已有环境变量时，`load_dotenv()` 默认不会覆盖它 | 创建 `task03/.env`，确认 `SILICONFLOW_API_BASE` 是完整 URL；运行时使用 `env -u MODEL_NAME -u SILICONFLOW_API_BASE uv run python agent.py` 清除旧变量 |
| 不确定 Agent 是否真的调用了文件工具 | 代码只打印了最终消息 `result["messages"][-1].content` | 遍历 `result["messages"]`，观察 `HumanMessage`、`AIMessage`、`ToolMessage` 和 `tool_calls` |
| 误把 `write_file` 和 `edit_file` 当成同一种操作 | 没有区分完整覆盖和局部修改 | `write_file` 用于新建或完整覆盖；`edit_file` 用于精确局部替换 |

## 六、和下一章的连接

第 3 章解决“信息放在哪里、如何取回”，第 4 章解决“复杂任务如何拆解和推进”。完成本章后，重点观察：

```text
任务规划产生的中间结果
        ↓
写入文件系统，避免全部占用上下文
        ↓
后续步骤按需读取并继续执行
```

这会把“Todo 规划”和“文件系统记忆”连接起来。

## 七、互动学习过程记录

本次学习采用“先回答、再验证、最后运行”的方式，没有直接跳过概念理解。

### 1. Context 与虚拟文件系统

我的回答要点：如果把所有资料和搜索结果都放进对话历史，context 会膨胀，模型的注意力会被大量无关信息分散。虚拟文件系统像 Agent 的资料库，把内容保存起来，需要时再加载，让模型专注于当前任务。

修正后的理解：

```text
模型上下文：当前正在思考和处理的内容
虚拟文件系统：暂时不放进上下文，但可以按需取回的资料和中间结果
```

### 2. 文件工具的分工

我完成了以下判断：

```text
ls         查看目录
read_file  读取文件内容
write_file 新建或完整覆盖文件
edit_file  精确修改文件局部内容
delete     删除文件或目录
glob       按路径模式查找文件
grep       按内容查找匹配项
```

关键区分：

- `glob` 关注“文件在哪里”；
- `grep` 关注“内容出现在哪里”；
- `write_file` 是完整重写；
- `edit_file` 是局部修改。

### 3. Agent 如何调用工具

实际运行后，观察到的调用序列是：

```text
ls → glob → read_file → grep → read_file → edit_file → read_file
```

对调用序列的分析：

1. `ls` 先观察当前工作区。
2. `glob` 按路径模式寻找相关文件。
3. `read_file` 读取原始资料。
4. `grep` 搜索 `Backend`、`context` 等关键词。
5. 再次 `read_file` 获取需要整理或检查的内容。
6. `edit_file` 修改已经存在的总结文件。
7. 最后 `read_file` 验证修改结果。

这次没有观察到 `write_file`，原因是 `ch03-summary.md` 在此前运行中已经存在，模型根据工作区状态选择了局部编辑。为了观察新建文件，可以让任务写入一个全新的文件名，不需要先删除旧文件。

### 4. Python 调试语法

为了观察消息链，我学习了以下写法：

```python
for message in result["messages"]:
    print("消息类型：", type(message).__name__)
    print("消息内容：", message.content)
    print("工具调用：", getattr(message, "tool_calls", []))
```

观察到的消息类型：

```text
HumanMessage：用户输入
AIMessage：模型输出，可能包含 tool_calls
ToolMessage：工具执行结果
```

### 5. Backend 的选择

完成的场景判断：

```text
临时计算过程       → StateBackend
本地项目文件       → FilesystemBackend
跨会话用户偏好     → StoreBackend
临时状态 + 长期记忆 → CompositeBackend
```

补充理解：`StateBackend` 适合当前 thread 的临时状态；`FilesystemBackend` 写入本地磁盘；`StoreBackend` 用于跨会话持久化，并且需要通过 namespace 做数据隔离。

### 6. 上下文自动管理

当工具结果过大时：

```text
完整结果写入 Backend
→ 对话中只留下文件路径和预览
→ Agent 需要时用 read_file 或 grep 取回
```

当长对话接近上下文窗口时：

```text
保存旧消息
→ 生成结构化摘要
→ 模型看到摘要和近期消息
```

这两种机制都减少当前模型输入，但目的不同：前者处理单次工具结果过大，后者处理整个对话历史过长。

### 7. 配置与安全结论

本次实验遇到的配置问题最终定位为 Base URL 没有被程序有效读取。修复后，Agent 成功创建总结文件：

```text
learning/task03/workspace/ch03-summary.md
```

当前实验配置的安全边界是：

```python
FilesystemBackend(
    root_dir=str(WORKSPACE),
    virtual_mode=True,
)
```

不能只依赖 `system_prompt` 约束模型。生产环境还应限制敏感路径、配置 `FilesystemPermission`，并避免把密钥、生产配置放进 Agent 可访问的工作区；`virtual_mode=True` 也不等于 Shell 命令沙箱。

## 八、本次学习结论

本章最终形成的工作模型是：

```text
模型负责决定调用什么工具
Backend 负责执行文件操作
文件系统保存资料和中间结果
上下文管理机制控制模型当前看到的内容
权限和沙箱负责安全边界
```

第 3 章已完成。下一章学习任务规划时，重点观察 Todo 产生的中间结果如何与本章的文件系统配合。
