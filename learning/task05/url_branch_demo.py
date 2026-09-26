"""Task 05：用 LangGraph 实现“是否存在 URL”的确定性分支。"""

from typing import NotRequired
import json
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from html import unescape
from pydantic import BaseModel, Field

class VerificationState(MessagesState):
    """图在执行过程中需要维护的状态。"""
    has_url: NotRequired[bool]
    url: NotRequired[str]
    source_text: NotRequired[str]
    route: NotRequired[str]
    content_supported: NotRequired[bool]
    status_code: NotRequired[int]
    final_url: NotRequired[str]
    evidence_snippets: NotRequired[dict[str, str]]

class VerificationReport(BaseModel):
    route: str
    url_present: bool
    source_url: str = ""
    http_status: int | None = None
    final_url: str = ""
    checked_keywords: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    evidence_snippets: dict[str, str] = Field(default_factory=dict)
    semantic_verification: str = "not_performed"
    error: str | None = None

def check_content(state: VerificationState) -> dict[str, object]:
    source_text = state.get("source_text", "").lower()

    # 请求失败时保留原来的失败状态
    if not source_text:
        return {
            "route": state.get("route", "fetch_failed"),
        }

    keywords = ["subagent", "context"]
    matched = [word for word in keywords if word in source_text]
    missing = [word for word in keywords if word not in source_text]

    supported = not missing

    evidence_terms = [
        "context quarantine",
        "context isolation",
        "final result",
        "concise result",
        "tool calls",
        "intermediate results",
    ]

    clean_text = re.sub(
        r"<(script|style|noscript).*?>.*?</\1>",
        " ",
        source_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    clean_text = re.sub(r"<[^>]+>", " ", clean_text)
    clean_text = unescape(clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    evidence_snippets = {}

    for term in evidence_terms:
        position = clean_text.lower().find(term.lower())

        if position != -1:
            start = max(0, position - 120)
            end = min(len(clean_text), position + len(term) + 180)
            evidence_snippets[term] = clean_text[start:end]

    report = {
        "route": "content_checked",
        "url_present": True,
        "source_url": state.get("url", ""),
        "http_status": state.get("status_code"),
        "final_url": state.get("final_url", ""),
        "checked_keywords": keywords,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "evidence_snippets": evidence_snippets,
        "semantic_verification": "not_performed",
    }

    return {
        "route": "content_checked",
        "content_supported": supported,
        "evidence_snippets": evidence_snippets,
        "messages": [
            AIMessage(
                content=json.dumps(report, ensure_ascii=False)
            )
        ],
    }

def inspect_source(state: VerificationState) -> dict[str, object]:
    """从最新一条消息中确定是否出现 URL。"""

    report = state["messages"][-1].content
    urls = re.findall(r"https?://[^\s]+", report)

    if not urls:
        return {
            "has_url": False,
            "url": "",
        }

    url = urls[0].rstrip(".,，。)")
    return {
        "has_url": True,
        "url": url,
    }


def choose_route(state: VerificationState) -> str:
    """根据状态选择下一节点，而不是让模型临时决定。"""

    return "fetch_source" if state.get("has_url") else "search_more"


def fetch_source(state: VerificationState) -> dict[str, object]:
    url = state.get("url", "")

    try:
        request = Request(
            url,
            headers={"User-Agent": "task05-source-checker/1.0"},
        )

        with urlopen(request, timeout=10) as response:
            body = response.read(1_000_000)
            status = response.status
            final_url = response.geturl()

        source_text = body.decode("utf-8", errors="replace")

    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        status = exc.code if isinstance(exc, HTTPError) else None

        report = VerificationReport(
            route="fetch_failed",
            url_present=bool(url),
            source_url=url,
            http_status=status,
            semantic_verification="not_performed",
            error=f"{type(exc).__name__}: {exc}",
        )

        return {
            "route": "fetch_failed",
            "messages": [
                AIMessage(
                    content=report.model_dump_json(ensure_ascii=False)
                )
            ],
        }

    return {
        "route": "fetched",
        "source_text": source_text,
        "status_code": status,
        "final_url": final_url,
        "messages": [
            AIMessage(
                content=(
                    f"来源可以访问：HTTP {status}\n"
                    f"最终 URL：{final_url}\n"
                    f"页面长度：{len(source_text)} 字符"
                )
            )
        ],
    }


def search_more(state: VerificationState) -> dict[str, object]:
    report = VerificationReport(
        route="search_more",
        url_present=False,
        semantic_verification="not_performed",
    )

    return {
        "route": "search_more",
        "messages": [
            AIMessage(
                content=report.model_dump_json(ensure_ascii=False)
            )
        ],
    }


builder = StateGraph(VerificationState)
builder.add_node("inspect_source", inspect_source)
builder.add_node("fetch_source", fetch_source)
builder.add_node("search_more", search_more)
builder.add_node("check_content", check_content)
builder.add_edge(START, "inspect_source")
builder.add_conditional_edges(
    "inspect_source",
    choose_route,
    {
        "fetch_source": "fetch_source",
        "search_more": "search_more",
    },
)
builder.add_edge("fetch_source", "check_content")
builder.add_edge("check_content", END)
builder.add_edge("search_more", END)

verification_graph = builder.compile()


def run_case(label: str, report: str) -> None:
    result = verification_graph.invoke(
        {"messages": [HumanMessage(content=report)]}
    )

    raw_result = result["messages"][-1].content
    validated_report = VerificationReport.model_validate_json(raw_result)

    print(f"{label}: route={validated_report.route}")
    print(validated_report.model_dump_json(ensure_ascii=False))


if __name__ == "__main__":
    run_case(
        "有 URL",
        "Context Quarantine 会隔离子 Agent 的中间过程。来源：https://docs.langchain.com/oss/python/deepagents/subagents",
    )
    run_case(
        "无 URL",
        "Context Quarantine 会隔离子 Agent 的中间过程。",
    )
    run_case(
    "访问失败",
    "Context Quarantine 的来源是：http://127.0.0.1:1/not-running",
    )
