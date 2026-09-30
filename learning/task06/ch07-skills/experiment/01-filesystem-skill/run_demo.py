"""Experiment 01: observe progressive Skill loading with FilesystemBackend."""

from pathlib import Path
import os

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


EXPERIMENT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_ROOT.parents[4]

load_dotenv(REPO_ROOT / "learning/task06/ch07-skills/.env", override=True)
load_dotenv(REPO_ROOT / "learning/task06/.env", override=True)

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "gpt-4.1-mini"),
    api_key=os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("SILICONFLOW_API_BASE", "https://api.openai.com/v1"),
)

backend = FilesystemBackend(
    root_dir=EXPERIMENT_ROOT,
    virtual_mode=True,
)

agent = create_deep_agent(
    model=model,
    backend=backend,
    skills=["/skills/"],
    system_prompt=(
        "这是 Skills 学习实验。处理 PR 审查任务时遵守 pr-review Skill。"
        "请在回答中简短列出你实际读取过的 Skill 文件路径；"
        "不要声称执行了当前 Backend 不支持执行的脚本。"
    ),
)


def main() -> None:
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请审查 /sample.diff。先总结变更，再检查是否涉及安全风险；"
                        "如果需要安全清单，请读取对应 references 文件。"
                        "最后给出带证据的位置、严重程度和建议。"
                    ),
                }
            ]
        },
        config={"configurable": {"thread_id": "task06-ch07-filesystem-skill"}},
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
