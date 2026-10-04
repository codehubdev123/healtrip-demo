from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage

from agent import run_healtrip_agent
import config

app = FastAPI(title="HealTrip AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessagePayload(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    user_input: str
    chat_history: Optional[List[ChatMessagePayload]] = []


@app.get("/")
def welcome():
    return {"status": 200, "message": "Wokring"}


@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    try:
        # Convert frontend payload list into LangChain Message objects
        # تحويل سجل الرسائل الممرض إلى كائنات LangChain معتمدة
        formatted_history = []
        for msg in request.chat_history:
            if msg.role == "user":
                formatted_history.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                formatted_history.append(AIMessage(content=msg.content))

        # Pass formatted history to agent
        structured_reply = run_healtrip_agent(
            user_input=request.user_input, chat_history=formatted_history
        )

        return structured_reply

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
