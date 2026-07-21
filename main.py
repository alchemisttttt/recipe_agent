from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agent import run_agent, SYSTEM_PROMPT


app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

history=[{"role":"system","content":SYSTEM_PROMPT}]

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    reply=run_agent(request.message,history)
    return {"reply":reply}

@app.get("/")
def root():
    return FileResponse("index.html")
