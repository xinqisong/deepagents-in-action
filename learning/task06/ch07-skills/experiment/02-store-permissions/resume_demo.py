"""Resume the permission experiment after approving the personal Skill edit."""

from demo import TenantContext, agent
from langgraph.types import Command


THREAD_ID = "task06-ch07-store-permissions-resume"
CONTEXT = TenantContext(org_id="org-acme", user_id="alice")
CONFIG = {"configurable": {"thread_id": THREAD_ID}}


def main() -> None:
    first = agent.invoke(
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
    print("=== first interrupt ===")
    print(first.get("__interrupt__"))

    resumed = agent.invoke(
        Command(resume={"decisions": [{"type": "approve"}]}),
        context=CONTEXT,
        config=CONFIG,
    )
    print("=== after approving personal Skill edit ===")
    print(resumed)


if __name__ == "__main__":
    main()
