import asyncio
from pprint import pprint

from langgraph_sdk import get_client

client = get_client(url="http://127.0.0.1:2024")
ASSISTANT_ID = "supervisor"

async def send(thread_id: str, content: str) -> None:
    result = await client.runs.wait(
        thread_id,
        ASSISTANT_ID,
        input={"messages": [{"role": "user", "content": content}]},
    )
    pprint(result)

async def main() -> None:
    thread = await client.threads.create()
    thread_id = thread["thread_id"]

    print("=== 1. 启动两个后台任务 ===")
    await send(
        thread_id,
        "请启动第一个后台 researcher 任务，研究 async subagent 的生命周期。",
    )


    await send(
        thread_id,
        "请再启动第二个后台 researcher 任务，研究 async subagent 的状态查询。",
    )

    print("=== 2. 取消前查看任务总览 ===")
    await send(thread_id, "请列出当前所有后台任务及其状态。")
    print("=== 3. 取消第一个任务 ===")
    await send(
        thread_id,
        "请立即取消第一个后台任务，不要等待它完成。",
    )

    print("=== 4. 查询被取消的任务 ===")
    await send(
        thread_id,
        "请查询刚才那个任务的最新状态。",
    )

    print("=== 5. 查看全部任务 ===")
    await send(
        thread_id,
        "请列出当前所有后台任务及其状态。",
    )


if __name__ == "__main__":
    asyncio.run(main())