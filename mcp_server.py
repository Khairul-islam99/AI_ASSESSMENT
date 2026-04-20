import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from datetime import datetime
import dateutil.parser
from langchain_ollama import ChatOllama

load_dotenv()
mcp = FastMCP("MyMCPServer")

@mcp.tool()
def get_current_time():
    """Return current UTC time and a human-readable phrase."""
    now = datetime.now()
    return f"UTC: {datetime.utcnow().isoformat()}Z, Local: {now.strftime('%A, %I:%M %p')}"

@mcp.tool()
def date_diff(date_a: str, date_b: str):
    """Return difference in days, hours, and minutes between two dates."""
    try:
        diff = abs(dateutil.parser.isoparse(date_a) - dateutil.parser.isoparse(date_b))
        return {"days": diff.days, "hours": diff.seconds // 3600, "minutes": (diff.seconds % 3600) // 60}

@mcp.tool()
def summarize_results(json_data: str, goal: str):
    """Accepts JSON data and a goal, returns a short summary using the LLM model."""
    try:
        llm = ChatOllama(base_url=os.getenv("OLLAMA_BASE_URL"), model=os.getenv("OLLAMA_MODEL"))
        prompt = f"Goal: {goal}\nData: {json_data}\nWrite a short, 1-paragraph summary."
        response = llm.invoke(prompt)
        return response.content

if __name__ == "__main__":
    mcp.run(transport='sse')