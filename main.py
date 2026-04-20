from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent import chat_with_ai, stream_chat_with_ai, my_tools

app = FastAPI()

class UserMessage(BaseModel):
    message: str

@app.get("/")
def home():
    return {"message": "AI Assessment Project Running"}

@app.get("/health")
def health():
    try:
        reply = chat_with_ai("Hello,Active")
        
        return {
            "status": "OK", 
            "database": "Connected", 
            "model_status": "Active",
            "ai_response": reply
        }
    except Exception as e:  #Ollama connection or other issues
        return {
            "status": "Failed",
            "model_status": "Offline or Error",
            "error_message": str(e)
        }

@app.get("/tools")
def show_tools():
    return [{"tool_name": t.name, "description": t.description} for t in my_tools]

@app.post("/chat")
def chat(user: UserMessage):
    reply = chat_with_ai(user.message)
    return {"user_msg": user.message, "AI ans": reply}

@app.post("/chat/stream")
async def chat_stream(user: UserMessage):
    return StreamingResponse(
        stream_chat_with_ai(user.message), 
        media_type="text/event-stream"
    )