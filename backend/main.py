import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CareerCompass API")

# Setup CORS so the React frontend can communicate with it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini AI
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # Using a modern model recommended for chat
    # system_instruction is used to keep the bot focused on career advice
    system_prompt = os.getenv(
        "SYSTEM_PROMPT", 
        "You are CareerCompass, a knowledgeable, empathetic, and professional AI career advisor. Your goal is to provide insightful career advice, interview tips, resume feedback, and professional development guidance. If a user asks about topics completely unrelated to careers, politely steer the conversation back to professional topics. Keep your answers clear, concise, and helpful."
    )
    model = genai.GenerativeModel('gemini-flash-latest', system_instruction=system_prompt)
else:
    model = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not model:
         raise HTTPException(status_code=500, detail="Gemini API Key is missing. Please set GEMINI_API_KEY in backend/.env")
    
    try:
        # For simplicity, this is a single turn interaction. 
        # In a full app, you might want to maintain a ChatSession or send the full history.
        response = model.generate_content(request.message)
        return ChatResponse(reply=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
