import os

from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver


load_dotenv()

model = ChatOpenAI(
    model=os.environ["MODEL_NAME"],
    api_key=os.environ["SILICONFLOW_API_KEY"],
    base_url=os.environ["SILICONFLOW_API_BASE"],
)

checkpointer = InMemorySaver()

agent = create_deep_agent(
    model=model,
    middleware=[TodoListMiddleware()],
    checkpointer=checkpointer,
    system_prompt="""
你正在学习 Checkpointer。
当用户要求规划复杂任务时，使用 write_todos 创建任务清单。
如果用户要求只规划，就不要执行后续任务。
""",
)

config = {
    "configurable": {
        "thread_id": "website-homepage-001",
    }
}

agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": """
请为“课程网站首页设计”创建一个 3 步任务计划。
只创建计划，不要执行任务。
""",
            }
        ]
    },
    config=config,
)

state_after_first_run = agent.get_state(config)

print("第一次运行后的 todos：")
print(state_after_first_run.values.get("todos", []))
print("第一次运行后的消息数量：")
print(len(state_after_first_run.values.get("messages", [])))


config = {
    "configurable": {
        "thread_id": "website-homepage-002",
    }
}

print("新 thread 调用前的状态：")
print(agent.get_state(config).values)

agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": """
继续刚才的网站首页设计任务，只执行第一个待办步骤。
""",
            }
        ]
    },
    config=config,
)

state_after_second_run = agent.get_state(config)

print("第二次运行后的 todos：")
print(state_after_second_run.values.get("todos", []))
print("第二次运行后的消息数量：")
print(len(state_after_second_run.values.get("messages", [])))

fresh_agent = create_deep_agent(
    model=model,
    middleware=[TodoListMiddleware()],
    checkpointer=InMemorySaver(),
)

original_config = {
    "configurable": {
        "thread_id": "website-homepage-001",
    }
}

print("原 Checkpointer 中的任务：")
print(agent.get_state(original_config).values.get("todos", []))

print("新 Checkpointer 中同名 thread 的状态：")
print(fresh_agent.get_state(original_config).values)