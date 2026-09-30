"""Approve only the write paths explicitly authorized in this lesson."""

from demo import TenantContext, agent
from langgraph.types import Command


THREAD_ID = "task06-ch07-store-permissions-consented-writes"
CONTEXT = TenantContext(org_id="org-acme", user_id="alice")
CONFIG = {"configurable": {"thread_id": THREAD_ID}}
APPROVED_PREFIXES = ("/skills/personal/", "/reports/")


def pending_actions(result: dict) -> list[dict]:
    actions = []
    for interrupt in result.get("__interrupt__", []):
        actions.extend(interrupt.value.get("action_requests", []))
    return actions


def resume_approved(result: dict) -> dict:
    actions = pending_actions(result)
    paths = [action["args"].get("file_path", "") for action in actions]
    print("approving:", list(zip([action["name"] for action in actions], paths)))
    if not actions or any(not path.startswith(APPROVED_PREFIXES) for path in paths):
        raise RuntimeError(f"Unexpected pending actions: {paths}")
    return agent.invoke(
        Command(resume={"decisions": [{"type": "approve"}] * len(actions)}),
        context=CONTEXT,
        config=CONFIG,
    )


def main() -> None:
    result = agent.invoke(
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
    for _ in range(5):
        actions = pending_actions(result)
        if not actions:
            print("completed without a pending approval")
            print(result)
            return
        result = resume_approved(result)
    raise RuntimeError("Too many approval rounds")


if __name__ == "__main__":
    main()
