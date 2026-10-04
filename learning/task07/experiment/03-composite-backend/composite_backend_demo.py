"""验证 CompositeBackend 的路径路由和 memory=加载，不调用真实模型。"""

from dataclasses import dataclass
from typing import Any

from pydantic import PrivateAttr
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from deepagents.backends.utils import create_file_data
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore


@dataclass(frozen=True)
class UserContext:
    user_id: str


class RecordingFakeModel(FakeListChatModel):
    """返回固定答案，同时记录 Agent 实际发送给模型的消息。"""

    _last_messages: list[BaseMessage] = PrivateAttr(default_factory=list)

    def _generate(self, messages: list[BaseMessage], **kwargs: Any):
        self._last_messages = list(messages)
        return super()._generate(messages, **kwargs)

    def bind_tools(self, tools: Any, **kwargs: Any):
        return self


def content_as_text(content: Any) -> str:
    """兼容字符串和 content block，便于检查 system prompt。"""

    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                parts.append(str(block.get("text", "")))
            else:
                parts.append(str(block))
        return "\n".join(parts)
    return str(content)


def main() -> None:
    store = InMemoryStore()
    namespace = ("user-a", "memories")
    memory_path = "/memories/preferences.md"
    store_key = "/preferences.md"

    # CompositeBackend 挂载 /memories/ 后，会去掉这个路由前缀再访问 Store。
    store.put(
        namespace,
        store_key,
        create_file_data("# 用户偏好\n- 中文注释\n- 英文变量名\n"),
    )

    backend = CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(
                namespace=lambda _runtime: namespace,
            ),
        },
    )
    model = RecordingFakeModel(responses=["fake-model-ok"])
    agent = create_deep_agent(
        model=model,
        context_schema=UserContext,
        memory=[memory_path],
        store=store,
        checkpointer=InMemorySaver(),
        backend=backend,
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "读取我的偏好。"}]},
        context=UserContext(user_id="user-a"),
        config={"configurable": {"thread_id": "composite-demo-1"}},
    )

    system_prompt = "\n".join(
        content_as_text(message.content)
        for message in model._last_messages
        if message.type == "system"
    )

    print(f"Agent path : {memory_path}")
    print(f"Store key  : {store_key}")
    print(f"namespace  : {namespace}")
    print(f"loaded     : {'中文注释' in system_prompt and '英文变量名' in system_prompt}")
    print(f"model reply: {result['messages'][-1].content}")

    assert "中文注释" in system_prompt
    assert "英文变量名" in system_prompt
    assert result["messages"][-1].content == "fake-model-ok"
    print("PASS: CompositeBackend 路由并加载了 Store 中的长期记忆。")


if __name__ == "__main__":
    main()
