"""Approve the report write and the follow-up correction."""

from demo import TenantContext, agent
from langgraph.types import Command


THREAD_ID = "task06-ch07-store-permissions-approve-correction"
CONTEXT = TenantContext(org_id="org-acme", user_id="alice")
CONFIG = {"configurable": {"thread_id": THREAD_ID}}


def approve_once() -> dict:
    return agent.invoke(
        Command(resume={"decisions": [{"type": "approve"}]}),
        context=CONTEXT,
        config=CONFIG,
    )


def main() -> None:
    agent.invoke(
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
    approve_once()  # personal Skill edit
    report_result = approve_once()  # report write
    print("report write resumed; next interrupt:", bool(report_result.get("__interrupt__")))
    final = approve_once()  # report correction
    print("final interrupt:", bool(final.get("__interrupt__")))
    print(final)


if __name__ == "__main__":
    main()
