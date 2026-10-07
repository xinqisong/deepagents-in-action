# Human-in-the-Loop Resources

## Knowledge

- [Datawhale 第 9 章](https://datawhalechina.github.io/deepagents-in-action/chapters/ch09-human-in-the-loop/)
  中文主线：工具审批、恢复、子 Agent、权限与底层中断；用来确定本章范围。本地对应 `content/ch09-human-in-the-loop.md`。
- [Deep Agents 官方：Human-in-the-loop](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop)
  用来核对 `interrupt_on`、条件 `when` 与子 Agent 的配置入口。
- [LangChain 官方：Human-in-the-loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
  用来核对四种 decision、审批 payload、批次顺序及 `edited_action` 的结构。
- [LangGraph 官方：Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
  用来核对恢复值、节点重放、幂等与并行中断。是学习运行原理时的首选资料。
- [DeepSeek 官方：Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode/)
  用来核对真实模型的思考模式开关及工具调用时 reasoning_content 的回传要求。本次基础审批练习显式使用非思考模式。

## Wisdom (Communities)

当前先完成本地练习；遇到真实集成问题再选择社区案例，不将阅读资料当作实践经验。

## 版本依据

2026-10-07 读取 `learning/task07/uv.lock` 并通过该目录 `.venv/bin/python` 查询安装元数据：

- deepagents：0.7.21
- langchain：1.4.3
- langgraph：1.2.12

已确认本地 `InterruptOnConfig` 包含 `when` 字段。未运行本章完整审批实验，不能据此声称所有分支行为都已验证。

## Gaps

- 已通过真实模型实验观察 `version="v2"` 返回的 `action_requests` 使用 `args` 字段；其余入口仍应按实际返回结构处理，不混用字段名。
- 内存 Checkpointer 只用于当前进程练习；跨进程恢复需要持久化后端，暂不宣称已完成生产验证。
