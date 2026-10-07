"""观察 interrupt() 恢复时如何重放节点。"""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    approved: bool


def main():
    events = []

    def approval_node(state: State) -> State:
        events.append("进入审批节点")
        approved = interrupt("批准这次模拟操作吗？")
        if approved:
            events.append("审批后执行模拟操作")
        return {"approved": bool(approved)}

    builder = StateGraph(State)
    builder.add_node("approval", approval_node)
    builder.add_edge(START, "approval")
    builder.add_edge("approval", END)
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "ch09-replay-03"}}

    paused = graph.invoke({"approved": False}, config=config, version="v2")
    print("暂停时，中断数量：", len(paused.interrupts))
    print("暂停时，事件：", events)

    resumed = graph.invoke(Command(resume=True), config=config, version="v2")
    print("恢复后，中断数量：", len(resumed.interrupts))
    print("恢复后，事件：", events)
    print("恢复后，approved：", resumed.value["approved"])


if __name__ == "__main__":
    main()
