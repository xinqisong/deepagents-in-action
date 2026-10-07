"""Deterministic tool calls for reviewing the full demo without a model key."""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

BRIEF_TITLE = "研究 Agent 的委派与安全发布"
BRIEF_BODY = (
    "## 已核实发现\n"
    "- 模板包含 research-agent。来源：source-01.md。\n"
    "- 敏感工具调用前可暂停审批。来源：source-02.md。\n"
    "## 待确认事项\n"
    "- 实际部署方式尚未指定。\n"
    "## 来源\n"
    "- source-01.md\n- source-02.md"
)


class ScriptedModel(BaseChatModel):
    calls: int = 0

    @property
    def _llm_type(self) -> str:
        return "task08-scripted-model"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.calls += 1
        if self.calls == 1:
            message = AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "task",
                        "args": {
                            "description": "读取两份课程资料，返回带来源的发现。",
                            "subagent_type": "research-agent",
                        },
                        "id": "delegate",
                    }
                ],
            )
        elif self.calls == 2:
            message = AIMessage(
                content="",
                tool_calls=[{"name": "list_course_sources", "args": {}, "id": "list"}],
            )
        elif self.calls == 3:
            message = AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "read_course_source",
                        "args": {"source_id": "source-01.md"},
                        "id": "read-1",
                    },
                    {
                        "name": "read_course_source",
                        "args": {"source_id": "source-02.md"},
                        "id": "read-2",
                    },
                ],
            )
        elif self.calls == 4:
            message = AIMessage(
                content="已查证：模板有 research-agent（source-01.md）；工具审批见 source-02.md。"
            )
        elif self.calls == 5:
            message = AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "publish_brief",
                        "args": {"title": BRIEF_TITLE, "body": BRIEF_BODY},
                        "id": "publish",
                    }
                ],
            )
        else:
            message = AIMessage(content="本轮结束")
        return ChatResult(generations=[ChatGeneration(message=message)])
