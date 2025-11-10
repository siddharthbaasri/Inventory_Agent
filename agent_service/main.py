from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from orchestration_agent import OrchestrationAgent
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware

app_state: Dict[str, any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    app_state['agent'] = await OrchestrationAgent.create()
    try:
        yield  
    finally:
        await app_state['agent'].shutdown()

app = FastAPI(lifespan = lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (frontend URLs)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    reply_text = await app_state['agent'].run_agent(request.message)    
    return ChatResponse(reply=reply_text)
