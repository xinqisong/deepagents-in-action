"""Experiment 02: separate shared/personal Skill namespaces and write policies."""

from dataclasses import dataclass
from pathlib import Path
import os

from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from deepagents.backends.utils import create_file_data
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langgraph.store.memory import InMemoryStore


REPO_ROOT = Path(__file__).resolve().parents[5]
load_dotenv(REPO_ROOT / "learning/task06/ch07-skills/.env", override=True)
load_dotenv(REPO_ROOT / "learning/task06/.env", override=True)


@dataclass(frozen=True)
class TenantContext:
    org_id: str
    user_id: str


def shared_skill_namespace(runtime):
    return ("curated-skills", runtime.context.org_id)


def personal_skill_namespace(runtime):
    return ("user-skills", runtime.context.user_id)


store = InMemoryStore()
store.put(
    ("curated-skills", "org-acme"),
    "/shared-demo/SKILL.md",
    create_file_data(
        "---\n"
        "name: shared-demo\n"
        "description: 组织共享的只读演示 Skill。需要查看共享规范时使用。\n"
        "---\n\n"
        "# shared-demo\n\n共享内容由管理员维护。"
    ),
)
store.put(
    ("user-skills", "alice"),
    "/personal-demo/SKILL.md",
    create_file_data(
        "---\n"
        "name: personal-demo\n"
        "description: Alice 的个人演示 Skill。需要查看个人偏好时使用。\n"
        "---\n\n"
        "# personal-demo\n\n个人内容可以提出修改。"
    ),
)


model = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "gpt-4.1-mini"),
    api_key=os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("SILICONFLOW_API_BASE", "https://api.openai.com/v1"),
)

backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/skills/shared/": StoreBackend(
            namespace=shared_skill_namespace,
            store=store,
        ),
        "/skills/personal/": StoreBackend(
            namespace=personal_skill_namespace,
            store=store,
        ),
    },
)

agent = create_deep_agent(
    model=model,
    context_schema=TenantContext,
    backend=backend,
    store=store,
    skills=["/skills/shared/", "/skills/personal/"],
    permissions=[
        FilesystemPermission(
            operations=["write"],
            paths=["/skills/shared/**"],
            mode="deny",
        ),
        FilesystemPermission(
            operations=["write"],
            paths=["/skills/personal/**"],
            mode="interrupt",
        ),
        FilesystemPermission(
            operations=["write"],
            paths=["/reports/**"],
            mode="interrupt",
        ),
    ],
    checkpointer=MemorySaver(),
    system_prompt=(
        "这是 Skills 权限实验。先读取 shared 和 personal 两处可用 Skill。"
        "然后尝试修改 shared Skill、修改 personal Skill，并写入 /reports/policy.md。"
        "逐项说明哪个操作被拒绝、哪个操作触发人工审批，以及原因。"
    ),
)


def main() -> None:
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请完成权限实验：先列出并读取 shared 和 personal Skill，"
                        "再分别尝试把一句说明追加到两个 Skill，最后写一份"
                        "权限观察报告到 /reports/policy.md。"
                    ),
                }
            ]
        },
        context=TenantContext(org_id="org-acme", user_id="alice"),
        config={"configurable": {"thread_id": "task06-ch07-store-permissions"}},
    )
    print(result)


if __name__ == "__main__":
    main()
