"""观察 user、agent、organization 三种长期记忆作用域。"""

from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore


def read_content(store: InMemoryStore, namespace: tuple[str, str], key: str) -> str | None:
    item = store.get(namespace, key)
    if item is None:
        return None
    return item.value["content"]


def main() -> None:
    store = InMemoryStore()
    preferences_key = "/preferences.md"
    knowledge_key = "/knowledge.md"
    policy_key = "/compliance.md"

    user_a = ("user-a", "memories")
    user_b = ("user-b", "memories")
    agent_memory = ("assistant-researcher", "memories")
    organization_policy = ("org-acme", "policies")

    store.put(
        user_a,
        preferences_key,
        create_file_data("# 偏好\\n- 中文注释\\n"),
    )
    store.put(
        user_b,
        preferences_key,
        create_file_data("# 偏好\\n- 英文注释\\n"),
    )
    store.put(
        agent_memory,
        knowledge_key,
        create_file_data("# Agent 知识\\n- 项目使用 Python\\n"),
    )
    store.put(
        organization_policy,
        policy_key,
        create_file_data("# 组织策略\\n- 不得泄露内部定价\\n"),
    )

    assert "中文注释" in (read_content(store, user_a, preferences_key) or "")
    assert "英文注释" in (read_content(store, user_b, preferences_key) or "")
    assert "英文注释" not in (read_content(store, user_a, preferences_key) or "")
    assert "Python" in (read_content(store, agent_memory, knowledge_key) or "")
    assert "内部定价" in (
        read_content(store, organization_policy, policy_key) or ""
    )

    print("user-scoped:")
    print("  user-a:", repr(read_content(store, user_a, preferences_key)))
    print("  user-b:", repr(read_content(store, user_b, preferences_key)))
    print("  isolation: PASS")

    print("agent-scoped:")
    print("  namespace:", agent_memory)
    print("  shared knowledge:", repr(read_content(store, agent_memory, knowledge_key)))

    print("organization-scoped:")
    print(
        "  policy:",
        repr(read_content(store, organization_policy, policy_key)),
    )
    print("  note: namespace 隔离数据，不自动禁止写入。")
    print("PASS: 三种作用域的 namespace 边界符合预期。")


if __name__ == "__main__":
    main()
