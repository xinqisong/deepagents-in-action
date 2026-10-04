"""观察 InMemoryStore 的 namespace 隔离；不需要模型或网络。"""

from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore


def main() -> None:
    store = InMemoryStore()
    user_a = ("user-a", "memories")
    user_b = ("user-b", "memories")
    key = "/preferences.md"

    store.put(
        user_a,
        key,
        create_file_data("# 用户偏好\n- 中文注释\n- 英文变量名\n"),
    )

    saved_for_a = store.get(user_a, key)
    saved_for_b = store.get(user_b, key)

    assert saved_for_a is not None
    assert saved_for_a.value["content"] == "# 用户偏好\n- 中文注释\n- 英文变量名\n"
    assert saved_for_b is None

    print(f"namespace A: {user_a}")
    print(f"key         : {key}")
    print(f"user-a value: {saved_for_a.value['content']!r}")
    print(f"user-b value: {saved_for_b}")
    print("PASS: 不同 namespace 的同名 key 彼此隔离。")


if __name__ == "__main__":
    main()
