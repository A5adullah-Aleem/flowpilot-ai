from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.services.llm import llm


class AgentState(TypedDict):
    user_request: str
    execution_plan: str


def plan_task(state: AgentState):

    prompt = f"""
    You are an AI business automation planner.

    Analyze the following business request.

    Break it into clear, logical execution steps.

    Do not execute anything.
    Only generate an execution plan.

    User Request:
    {state['user_request']}
    """

    response = llm.invoke(prompt)

    return {
        "execution_plan": response.content
    }


graph_builder = StateGraph(AgentState)

graph_builder.add_node("planner", plan_task)

graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", END)

task_planner = graph_builder.compile()


def generate_plan(user_request: str):

    result = task_planner.invoke({
        "user_request": user_request,
        "execution_plan": "",
    })

    return result["execution_plan"]