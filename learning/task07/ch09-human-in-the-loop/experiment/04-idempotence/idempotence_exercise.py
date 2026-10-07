"""两次 interrupt() 展示重放下的重复追加与按操作 ID 覆盖。"""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    completed: bool


def main():
    append_log = []
    records_by_operation_id = {}
    operation_id = "language-change-001"

    def approval_node(state: State) -> State:
        approved = interrupt("批准将语言改为中文吗？")
        if not approved:
            return {"completed": False}

        append_log.append("language=中文")
        records_by_operation_id[operation_id] = "language=中文"
        confirmed = interrupt("确认这次模拟操作已完成吗？")
        return {"completed": bool(confirmed)}

    builder = StateGraph(State)
    builder.add_node("approval", approval_node)
    builder.add_edge(START, "approval")
    builder.add_edge("approval", END)
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "ch09-idempotence-04"}}

    paused = graph.invoke({"completed": False}, config=config, version="v2")
    print("首次暂停：", [item.value for item in paused.interrupts])
    print("首次暂停后的追加记录：", append_log)

    paused_again = graph.invoke(Command(resume=True), config=config, version="v2")
    print("第二次暂停：", [item.value for item in paused_again.interrupts])
    print("第二次暂停后的追加记录：", append_log)
    print("第二次暂停后的按 ID 保存记录：", records_by_operation_id)

    finished = graph.invoke(Command(resume=True), config=config, version="v2")
    print("完成后，中断数量：", len(finished.interrupts))
    print("完成后的追加记录：", append_log)
    print("完成后的按 ID 保存记录：", records_by_operation_id)


if __name__ == "__main__":
    main()
