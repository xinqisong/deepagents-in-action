"""观察 Checkpointer 如何按 thread_id 保存短期状态。"""

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState, START, StateGraph


def observe_messages(state: MessagesState) -> dict[str, list[AIMessage]]:
    """把当前 state 中的消息数量写回，方便观察是否恢复了历史。"""

    return {
        "messages": [
            AIMessage(content=f"observed_messages={len(state['messages'])}")
        ]
    }


def build_graph():
    builder = StateGraph(MessagesState)
    builder.add_node("observe_messages", observe_messages)
    builder.add_edge(START, "observe_messages")
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    thread_a = {"configurable": {"thread_id": "task07-user-a"}}
    thread_b = {"configurable": {"thread_id": "task07-user-b"}}

    first = graph.invoke(
        {"messages": [{"role": "user", "content": "我叫小林。"}]},
        config=thread_a,
    )
    second = graph.invoke(
        {"messages": [{"role": "user", "content": "我的名字是什么？"}]},
        config=thread_a,
    )
    other_thread = graph.invoke(
        {"messages": [{"role": "user", "content": "这是另一个对话。"}]},
        config=thread_b,
    )

    first_observation = first["messages"][-1].content
    second_observation = second["messages"][-1].content
    other_observation = other_thread["messages"][-1].content

    print(f"thread A / first call : {first_observation}")
    print(f"thread A / second call: {second_observation}")
    print(f"thread B / first call : {other_observation}")

    assert first_observation == "observed_messages=1"
    assert second_observation == "observed_messages=3"
    assert other_observation == "observed_messages=1"

    print("PASS: Checkpointer 按 thread_id 恢复短期状态。")


if __name__ == "__main__":
    main()
