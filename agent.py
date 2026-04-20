import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from datetime import datetime
import dateutil.parser

from db import query_database, list_tables, describe_table

load_dotenv()

base_llm = ChatOllama(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    model=os.getenv("OLLAMA_MODEL")
)

# Keep all original tools
@tool
def get_current_time():
    """Return current time."""
    return f"Time: {datetime.now().strftime('%A, %I:%M %p')}"

@tool
def date_diff(date_a: str, date_b: str):
    """Return difference between two dates."""
    try:
        diff = abs(dateutil.parser.isoparse(date_a) - dateutil.parser.isoparse(date_b))
        return {"days": diff.days}
    except Exception:
        return {"error": "Invalid date"}

@tool
def summarize_results(json_data: str, goal: str) :
    """Summarize JSON data based on the given goal."""
    prompt = f"Goal: {goal}\nData: {json_data}\nWrite a short, 1-paragraph summary."
    return base_llm.invoke([("user", prompt)]).content

my_tools = [query_database, list_tables, describe_table, get_current_time, date_diff, summarize_results]
ai_with_tools = base_llm.bind_tools(my_tools)

def ai_node(state: MessagesState):
    return {"messages": [ai_with_tools.invoke(state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("brain", ai_node)
builder.add_node("tools", ToolNode(my_tools))
builder.add_edge(START, "brain")
builder.add_conditional_edges("brain", tools_condition)
builder.add_edge("tools", "brain")
my_agent = builder.compile()

#system prompt
prompt = SystemMessage(content="""You are a helpful AI data analyst. you have access to tools that can query a database, list tables, and describe table schemas. Use these tools to answer user questions about the data. Always try to use the tools when needed,
                   and provide clear, concise answers based on the tool outputs.Always use the tools when the user asks about data or database structure. 
                   If the user asks for current time or date differences, use the respective tools. For summarization tasks, use the summarize_results tool. 
                   if user say descrie my dataset use tools then list tables and describe tables tools must be used""")

def chat_with_ai(user_text: str):
    result = my_agent.invoke({"messages": [prompt, ("user", user_text)]})
    return result["messages"][-1].content

async def stream_chat_with_ai(user_text: str):
    async for msg, metadata in my_agent.astream(
        {"messages": [prompt, ("user", user_text)]}, 
        stream_mode="messages"
    ):
        if msg.content:
            yield f"data: {msg.content}\n\n"