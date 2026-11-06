from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from app.services.llm import llm
from app.tools.calculator import calculator


# Register available tools
tools = [calculator]

# Give tools to the LLM
llm_with_tools = llm.bind_tools(tools)


# Agent node
def assistant(state: MessagesState):

    response = llm_with_tools.invoke(state["messages"])

    return {
        "messages": [response]
    }


# Build graph
builder = StateGraph(MessagesState)

builder.add_node("assistant", assistant)

builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")

builder.add_conditional_edges(
    "assistant",
    tools_condition,
)

builder.add_edge("tools", "assistant")

# Compile graph
agent = builder.compile()


def run_agent(user_request: str):

    result = agent.invoke({
        "messages": [
            HumanMessage(content=user_request)
        ]
    })

    return result["messages"][-1].content