"""Approve both interrupt points in the permission experiment."""

from demo import TenantContext, agent
from langgraph.types import Command


THREAD_ID = "task06-ch07-store-permissions-approve-report"
CONTEXT = TenantContext(org_id="org-acme", user_id="alice")
CONFIG = {"configurable": {"thread_id": THREAD_ID}}


def main() -> None:
    initial = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请读取 shared 和 personal Skill，尝试修改两个 Skill，"
                        "然后把权限观察报告写入 /reports/policy.md。"
                    ),
                }
            ]
        },
        context=CONTEXT,
        config=CONFIG,
    )
    print("initial interrupt:", bool(initial.get("__interrupt__")))

    after_personal_approval = agent.invoke(
        Command(resume={"decisions": [{"type": "approve"}]}),
        context=CONTEXT,
        config=CONFIG,
    )
    print(
        "report interrupt after personal approval:",
        bool(after_personal_approval.get("__interrupt__")),
    )

    final = agent.invoke(
        Command(resume={"decisions": [{"type": "approve"}]}),
        context=CONTEXT,
        config=CONFIG,
    )
    print("final state:")
    print(final)


if __name__ == "__main__":
    main()
