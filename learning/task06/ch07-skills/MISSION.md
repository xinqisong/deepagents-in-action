# Mission: Deep Agents Skills

## Why

把“我反复告诉 Agent 怎么做”变成可以发现、按需加载、复用和审计的能力包，并在当前 DeepAgents 版本中亲手做出一个可运行的 Skill。

## Success looks like

- 能用自己的话解释 `SKILL.md`、`description` 和渐进式披露的关系。
- 能区分 Skill、Memory（始终生效的上下文）和 Tool（原子可执行操作），并为一个任务做出选择。
- 能用 `FilesystemBackend` 或 `StateBackend` 加载一个本地 Skill，观察 Agent 何时读取正文和辅助资源。
- 能解释 `skills` 路径、同名 Skill 的 last-wins、子 Agent 继承与权限边界。
- 能完成一次从目录结构、frontmatter、执行脚本到结果验收的端到端实验。

## Constraints

- 沿用当前分支 `learning/task06`，不切换分支；task06 既有实验保持不动。
- 以本地虚拟环境为准：`deepagents==0.7.20`、`langgraph==1.2.12`、`langgraph-sdk==0.4.5`。
- 中文、短课、先回忆再看答案；每次只推进一个可观察行为。
- 不把真实密钥写入仓库；优先使用本地临时 Backend 和专用实验目录。

## Out of scope

- 本轮不展开长期记忆、MCP、动态子 Agent 和远程生产部署。
- 不把“会背 API”当作完成标准；必须能解释加载时机、状态边界和安全取舍。
