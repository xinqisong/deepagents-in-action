"""确定性地模拟长期记忆的覆盖冲突和事件整合。"""

from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore


def read_content(store: InMemoryStore, namespace: tuple[str, str], key: str) -> str:
    item = store.get(namespace, key)
    assert item is not None
    return item.value["content"]


def main() -> None:
    store = InMemoryStore()
    memory_namespace = ("assistant-researcher", "memories")
    events_namespace = ("assistant-researcher", "events")
    memory_key = "/AGENTS.md"

    base = "# Agent 知识\\n- 保持回答简洁。\\n"
    writer_a = base + "- 用户偏好中文说明。\\n"
    writer_b = base + "- 用户偏好代码示例。\\n"

    # 两个线程都基于同一份旧内容生成更新，B 最后写入同一个 key。
    store.put(memory_namespace, memory_key, create_file_data(writer_a))
    store.put(memory_namespace, memory_key, create_file_data(writer_b))
    overwritten = read_content(store, memory_namespace, memory_key)

    assert "代码示例" in overwritten
    assert "中文说明" not in overwritten
    print("same-file conflict:")
    print("  final:", repr(overwritten))
    print("  result: last-write-wins，writer A 的更新丢失")

    # 更安全的模式：对话中先写独立事件，整合阶段再合并。
    store.put(
        events_namespace,
        "/thread-a.md",
        create_file_data("- 用户偏好中文说明。\\n"),
    )
    store.put(
        events_namespace,
        "/thread-b.md",
        create_file_data("- 用户偏好代码示例。\\n"),
    )

    event_a = read_content(store, events_namespace, "/thread-a.md")
    event_b = read_content(store, events_namespace, "/thread-b.md")
    consolidated = base + event_a + event_b
    store.put(memory_namespace, memory_key, create_file_data(consolidated))
    merged = read_content(store, memory_namespace, memory_key)

    assert "中文说明" in merged
    assert "代码示例" in merged
    print("event-log consolidation:")
    print("  final:", repr(merged))
    print("  result: 两个事件都被保留")
    print("PASS: 理解覆盖冲突与后台整合的差异。")


if __name__ == "__main__":
    main()
