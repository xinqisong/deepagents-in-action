# Deep Agents Long-term Memory Resources

## Knowledge

- [Datawhale 第 8 章：长期记忆](https://datawhalechina.github.io/deepagents-in-action/chapters/ch08-long-term-memory/)

  本课程的主线、中文解释和实验顺序。优先用它建立整体地图，但遇到版本差异以官方文档和本地运行结果为准。

- [LangChain 官方：Deep Agents Memory](https://docs.langchain.com/oss/python/deepagents/memory)

  核对 `memory=`、`StoreBackend`、`CompositeBackend`、namespace、文件初始化、并发写入和生产升级路径。

- [LangGraph 官方：Memory](https://docs.langchain.com/oss/python/langgraph/add-memory)

  核对短期 thread persistence、`InMemorySaver`、长期 Store 以及数据库 checkpointer 的基础概念。

- [Deep Agents Python 源码](https://github.com/langchain-ai/deepagents)

  只在官方文档与本地版本行为不一致时，用于追踪实现细节；源码事实不能替代实验验证。

## Wisdom

暂不引入额外社区案例。先完成本地实验，再根据遇到的并发、权限或部署问题选择真实项目案例。

## Gaps

- 需要在本地确认 `deepagents==0.7.20` 下 `CompositeBackend` 与 `StoreBackend` 的具体签名。
- 需要分别记录“课程写法、官方当前写法、本地可运行写法”。
- 生产级 `PostgresStore` 只做概念核对，除非后续明确需要，否则不在本轮启动数据库。
