# Deep Agents Skills Resources

## Knowledge

- [Agent Skills Specification](https://agentskills.io/specification)

  Skills 的规范来源。用于核对目录结构、`SKILL.md` frontmatter 约束、可选的 `scripts/`、`references/`、`assets/` 和渐进式披露。

- [LangChain 官方：Skills](https://docs.langchain.com/oss/python/deepagents/skills)

  当前 DeepAgents Python API 的主资料。用于核对 `skills=`、`StateBackend`、`FilesystemBackend`、`StoreBackend`、技能覆盖顺序、子 Agent 和权限。

- [Datawhale 第 7 章：Skills](https://datawhalechina.github.io/deepagents-in-action/chapters/ch07-skills/)

  本课程的叙事、中文示例和实验顺序。遇到版本差异时，以当前官方文档和本地环境验证结果为准。

- [Deep Agents Python source](https://github.com/langchain-ai/deepagents)

  用于 API 行为和实现细节核对，不作为第一阅读材料；只在文档与本地运行结果不一致时查看。

## Wisdom

目前不引入额外社区。先通过本地实验和官方文档建立可复现的判断，再决定是否需要寻找社区案例。

## Gaps

- 当前课程页中的部分示例与本地 `deepagents==0.7.20` 的推荐装载 API 可能有差异；后端实验时需要记录“文档写法、实际签名、可运行写法”三者的关系。
