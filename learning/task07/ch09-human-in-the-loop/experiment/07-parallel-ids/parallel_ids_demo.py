"""两个并行节点各自中断；按 Interrupt.id 映射恢复值。"""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    publish_approved: bool
    archive_approved: bool


def main():
    def review_publish(state: State) -> dict:
        return {"publish_approved": bool(interrupt("publish"))}

    def review_archive(state: State) -> dict:
        return {"archive_approved": bool(interrupt("archive"))}

    builder = StateGraph(State)
    builder.add_node("review_publish", review_publish)
    builder.add_node("review_archive", review_archive)
    builder.add_edge(START, "review_publish")
    builder.add_edge(START, "review_archive")
    builder.add_edge("review_publish", END)
    builder.add_edge("review_archive", END)
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "ch09-parallel-ids-07"}}

    paused = graph.invoke(
        {"publish_approved": False, "archive_approved": False},
        config=config,
        version="v2",
    )
    print("独立中断数量：", len(paused.interrupts))
    for item in paused.interrupts:
        print("中断 ID 与问题：", item.id, item.value)

    answers = {"publish": True, "archive": False}
    resume_by_id = {item.id: answers[item.value] for item in paused.interrupts}
    resumed = graph.invoke(Command(resume=resume_by_id), config=config, version="v2")
    print("恢复后中断数量：", len(resumed.interrupts))
    print("恢复后状态：", resumed.value)


if __name__ == "__main__":
    main()
