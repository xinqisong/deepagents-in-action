"""用 LangGraph SDK 在同一个 thread 上验证 async task 生命周期。"""

import asyncio
from pprint import pprint

from langgraph_sdk import get_client


client = get_client(url="http://127.0.0.1:2024")
ASSISTANT_ID = "supervisor"


async def send(thread_id: str, content: str) -> dict:
    result = await client.runs.wait(
        thread_id,
        ASSISTANT_ID,
        input={"messages": [{"role": "user", "content": content}]},
    )
    pprint(result)
    return result

async def main() -> None:
    thread = await client.threads.create()
    thread_id = thread["thread_id"]
    print("thread_id =", thread_id)

    print("\n=== 1. 启动后台研究 ===")
    await send(
        thread_id,
        "请把这个任务交给 researcher 异步处理："
        "整理同步 SubAgent 和异步 SubAgent 的核心差异。",
    )

    print("\n=== 2. 后台运行期间，主 Agent 处理无关问题 ===")
    await send(
        thread_id,
        "先不要查询后台任务。请直接解释："
        "为什么异步任务需要 task_id？",
    )

    print("\n=== 3. 给原任务追加验收要求 ===")
    await send(
        thread_id,
        "请给刚才的 researcher 任务追加要求："
        "最终结果使用 3 条 bullet，总结核心结论，"
        "并明确标注哪些内容有证据支持。不要重新创建任务。",
    )

    print("\n等待 researcher 完成……")
    await asyncio.sleep(25)

    print("\n=== 4. 取回最终结果 ===")
    await send(
        thread_id,
        "请把刚才那个后台研究任务的最终结果取回来，"
        "并分别说明任务是否执行成功、报告内容是否满足验收要求。",
    )

if __name__ == "__main__":
    asyncio.run(main())

