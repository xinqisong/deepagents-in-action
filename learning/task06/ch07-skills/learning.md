# Task 07 学习记录：Skills

课程原文：

<https://datawhalechina.github.io/deepagents-in-action/chapters/ch07-skills/>

本目录的学习使命见 [MISSION.md](MISSION.md)，资料见 [RESOURCES.md](RESOURCES.md)。

## 起点判断

你已经完成：

- task03：虚拟文件系统、Backend、上下文卸载和权限风险；
- task04：规划、中间件、Checkpointer 与状态边界；
- task05：同步子 Agent、Context Quarantine、CompiledSubAgent；
- task06：异步子 Agent 的 start / check / update / cancel / list 生命周期。

因此本章不重新讲文件工具或子 Agent 基础，重点转向：如何把领域流程封装成 Agent 可以发现、按需读取和复用的能力包。

## 本章目标

完成后，你应该能够：

1. 用自己的话解释 Skill 的目录结构和 `SKILL.md` frontmatter；
2. 解释“元数据 → 指令正文 → 辅助资源”的渐进式披露，并指出每一层何时进入上下文；
3. 判断一个需求应该做成 Skill、Memory 还是 Tool；
4. 在当前 `deepagents==0.7.20` 环境中用至少一种 Backend 加载 Skill；
5. 验证多个 Skill 的同名覆盖、子 Agent 的 Skill 可见性和权限策略；
6. 区分“脚本能被读取”和“脚本能被安全执行”；
7. 写出一个短而具体、带触发条件的 `description`，并用实验验证它是否容易被正确路由。

## 学习路线

### Session 0：建立概念边界（现在，20 分钟）

目标：先不写代码，分清 Skill、Tool、Memory。

动作：

1. 阅读 [第一课](lessons/0001-progressive-disclosure.html)；
2. 遮住速查页的答案，回答三道回忆题；
3. 用一句话写出“为什么不把全部 `SKILL.md` 正文放进启动提示词”。

验收：能说出三层加载和它们的触发时机；能举出一个 Skill 而不是 Tool 的例子。

### Session 1：最小 Skill + FilesystemBackend（45–60 分钟）

目标：亲眼观察 Skill 元数据被发现、正文被读取。

实验：创建 `skills/report-review/SKILL.md`，只包含 frontmatter 和一个三步报告审查流程；使用专用 `FilesystemBackend(root_dir=..., virtual_mode=True)` 加载 `/skills/`。

验收：记录 Skill 目录树、`name` / `description`、Agent 是否读取正文，以及最终回答是否遵守流程。不要只看最终文本，要观察工具轨迹。

### Session 2：StateBackend 与渐进式披露（45–60 分钟）

目标：理解无磁盘注入与本地磁盘加载的差异。

实验：用 `create_file_data()` 将同一个 Skill 注入 `StateBackend`，比较“每次 invoke 传入 files”和“磁盘已有文件”两种生命周期。

验收：能解释为什么 `skills=["/skills/"]` 指向父目录，而不是直接指向某个 `SKILL.md`；能说明 raw string 为什么不能替代 `create_file_data()`。

### Session 3：多源、Store 与子 Agent（60–90 分钟）

目标：掌握可见性和优先级。

实验：准备 shared / project 两套同名 Skill，验证后者覆盖前者；再让自定义子 Agent 显式声明自己的 Skill，和通用子 Agent 的继承行为做对比。

验收：画出“主 Agent、通用子 Agent、自定义子 Agent、Skill 源”的可见性图，并解释为什么 last-wins 需要写进部署约定。

### Session 4：权限和安全边界（60–90 分钟）

目标：让共享 Skill 库可读但不可被 Agent 擅改。

实验：用 `CompositeBackend` + `StoreBackend` 挂载 `/skills/`，比较 `FilesystemPermission(mode="deny")` 和 `mode="interrupt"`；验证 read、write、edit、delete 的边界。

验收：完成一张“可发现 / 可读取 / 可写入 / 需审批”的权限矩阵，并解释 `interrupt` 为什么需要 checkpointer。

### Session 5：脚本、解释器和端到端 Skill（60–90 分钟）

目标：完成一个能复用、可验证的项目型 Skill。

实验：先做可读的 `scripts/` 资源，再讨论沙箱执行；如环境允许，再做一个 QuickJS 解释器 Skill，让 Agent import 经过测试的确定性函数。

验收：明确区分“指令让模型怎么做”“脚本提供确定性逻辑”“沙箱提供执行隔离”，并完成一次结果校验。

### Session 6：间隔复习与设计答辩（30–45 分钟）

不看资料回答：

1. Skill 为什么不是一个更大的 Tool？
2. `description` 为什么比正文更早影响路由？
3. 什么内容应该放进 Memory，什么内容应该按需放进 Skill？
4. FilesystemBackend、StateBackend、StoreBackend 的生命周期差异是什么？
5. 如何证明 Agent 真的读取了 Skill，而不是碰巧生成了看似正确的答案？
6. 为什么“能执行脚本”必须单独讨论沙箱和权限？

## 版本边界

课程章节的概念和本地环境一致，但 API 示例可能随版本变化。当前环境实际检测到：

```text
deepagents      0.7.20
langgraph       1.2.12
langgraph-sdk   0.4.5
langchain-openai 1.6.6
```

官方当前文档特别强调：`skills` 路径指向包含 Skill 子目录的父目录；`StateBackend` 需要通过 `files` 注入并使用 `create_file_data()`；本地 `FilesystemBackend` 应使用 `virtual_mode=True`。实验时以本地签名和运行结果为准，并把差异记录下来。

## 当前状态

- [x] 已读取第 7 章课程页和 Agent Skills 官方规范
- [x] 已读取当前 DeepAgents 官方 Skills 文档
- [x] 已建立 Mission、Resources、第一课和速查页
- [ ] 用户完成 Session 0 回忆题
- [ ] 用户证明能区分 Skill / Tool / Memory
- [ ] 完成最小 FilesystemBackend 实验
- [ ] 完成 StateBackend / Store / 权限实验
- [ ] 完成端到端 Skill 并通过答辩
