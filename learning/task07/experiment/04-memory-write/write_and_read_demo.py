"""验证 Agent 运行时写入长期记忆，并在新 thread 读取。"""

from dataclasses import dataclass
import os
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from deepagents.backends.utils import create_file_data
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore


@dataclass(frozen=True)
class UserContext:
    user_id: str


def user_memory_namespace(runtime) -> tuple[str, str]:
    return (runtime.context.user_id, "memories")


def build_agent(store: InMemoryStore):
    model_name = os.getenv("MODEL_NAME", "gpt-4.1-mini")
    api_key = os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("SILICONFLOW_API_BASE") or os.getenv("OPENAI_BASE_URL")

    if not api_key:
        raise RuntimeError(
            "缺少 API key。请先复制 .env.example 为 .env 并填写模型配置。"
        )

    model_kwargs = {"model": model_name, "api_key": api_key}
    if base_url:
        model_kwargs["base_url"] = base_url

    backend = CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(
                namespace=user_memory_namespace,
            ),
        },
    )

    return create_deep_agent(
        model=ChatOpenAI(**model_kwargs),
        context_schema=UserContext,
        store=store,
        checkpointer=InMemorySaver(),
        backend=backend,
        memory=["/memories/preferences.md"],
        system_prompt=(
            "这是长期记忆写入实验。"
            "当用户明确要求记住偏好时，先读取 /memories/preferences.md，"
            "再使用 edit_file 更新同一个文件；保留已有内容，不要另建文件，"
            "不要使用 write_file 覆盖整个文件。"
            "只有 Store 中确实出现新内容后，才告诉用户已经记住。"
        ),
    )


def main() -> None:
    task07_env = Path(__file__).resolve().parents[2] / ".env"
    task06_env = Path(__file__).resolve().parents[3] / "task06" / ".env"
    load_dotenv(task06_env)
    load_dotenv(task07_env, override=True)

    store = InMemoryStore()
    user = UserContext(user_id="user-123")
    namespace = (user.user_id, "memories")
    store_key = "/preferences.md"

    store.put(
        namespace,
        store_key,
        create_file_data("# 用户偏好\n暂无记录。\n"),
    )

    agent = build_agent(store)

    agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "请记住我的偏好：代码注释用中文，变量名用英文。",
                }
            ]
        },
        context=user,
        config={"configurable": {"thread_id": "memory-write-1"}},
    )

    saved = store.get(namespace, store_key)
    assert saved is not None, "Store 中没有找到偏好文件。"
    content = saved.value["content"]
    assert "变量" in content and "英文" in content

    print("write evidence: Store 断言通过")
    print(f"saved content: {content!r}")

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "根据我之前保存的编码偏好，简要说明你会如何命名变量。",
                }
            ]
        },
        context=user,
        config={"configurable": {"thread_id": "memory-read-new-thread"}},
    )

    assert store.get(("another-user", "memories"), store_key) is None
    print("cross-user isolation: PASS")
    print("new thread reply:")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
