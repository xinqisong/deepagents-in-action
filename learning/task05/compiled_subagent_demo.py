"""Task 05：把一个已编译的 LangChain Agent 接入 DeepAgents。"""

import os

from deepagents import create_deep_agent
from deepagents.profiles import (
    GeneralPurposeSubagentProfile,
    HarnessProfile,
    register_harness_profile,
)
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from url_branch_demo import verification_graph
from typing import Literal

from pydantic import BaseModel, Field
from langchain.agents.structured_output import ProviderStrategy

load_dotenv()


model = ChatOpenAI(
    model=os.environ["MODEL_NAME"],
    api_key=os.environ["SILICONFLOW_API_KEY"],
    base_url=os.environ["SILICONFLOW_API_BASE"],
)


register_harness_profile(
    key=f"openai:{os.environ['MODEL_NAME']}",
    profile=HarnessProfile(
        general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False),
    ),
)

class FactCheckReport(BaseModel):
    verdict: Literal[
        "supported",
        "partially_supported",
        "unsupported",
        "insufficient_evidence",
    ]

    supported_claims: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    cautions: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)

    risk_level: Literal["low", "medium", "high"]



compiled_url_router = {
    "name": "compiled-url-router",
    "description": (
        "检查研究报告是否包含 URL、URL 是否可访问，"
        "并对网页进行基础关键词检查。"
        "输出 URL 时必须使用纯文本，不要使用 Markdown 链接格式。"
        "不要输出 [URL](URL)，也不要改写 URL。"
    ),
    "runnable": verification_graph,
}

fact_checker = {
    "name": "fact_checker",
    "description": (
        "根据原始结论、来源 URL 和路由检查结果，"
        "判断证据是否足以支持结论。"
    ),
    "response_format": ProviderStrategy(FactCheckReport),
    "system_prompt": """
你是事实核验员。

请读取 compiled-url-router 返回的 JSON 和证据片段，判断原始结论是否成立。

要求：
- 只能依据输入中的证据；
- 不得补造来源；
- 关键词命中不等于结论成立；
- 如果证据只支持结论的一部分，verdict 使用 partially_supported；
- 如果证据不足，verdict 使用 insufficient_evidence；
- 注意区分 final result、concise result 和 summary；
- 注意区分同步 subagent 与异步 subagent 的范围。

请严格按照 FactCheckReport 字段返回结果。
""",
}

supervisor = create_deep_agent(
    model=model,
    system_prompt="""
你是协调者。

严格按以下顺序处理：

1. 只调用一次 compiled-url-router；
2. 记录它返回的完整结果；
3. 将原始研究结论、来源 URL 和 compiled-url-router 的完整结果传给 fact_checker；
4. 最终回答必须区分“检查结果”和“事实核验结论”。

不要把关键词命中直接当成事实成立。

compiled-url-router 只负责：
1. 判断是否存在 URL；
2. 检查 URL 是否可访问；
3. 检查固定关键词 ['subagent', 'context']。

收到结果后，直接转述：
- route
- HTTP 状态码
- 最终 URL
- 命中关键词
- 缺失关键词

必须明确说明：关键词命中不等于语义事实成立。
compiled-url-router 不负责真正的事实核验。

compiled-url-router 返回的是一个 JSON 对象。
必须按 JSON 字段读取结果，不要根据缺失字段自行推断。
semantic_verification 为 not_performed 时，表示尚未完成语义事实核验。
""",
    subagents=[compiled_url_router, fact_checker],
)


result = supervisor.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": """
请核验下面这份研究报告：

结论：Context Quarantine 可以隔离子 Agent 的中间工具调用，只把最终摘要返回给主 Agent。
来源：https://docs.langchain.com/oss/python/deepagents/subagents

请判断该来源是否足以支持结论，并指出需要谨慎表述的地方。
""",
            }
        ]
    }
)

for index, message in enumerate(result["messages"]):
    print(
        f"{index}: {type(message).__name__} "
        f"| name={getattr(message, 'name', '-')}"
    )

    for tool_call in getattr(message, "tool_calls", []):
        if tool_call.get("name") == "task":
            print("task 参数：")
            print(tool_call.get("args"))

print(result["messages"][-1].content)
