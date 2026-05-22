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
        # "SYSTEM_PROMPT", 
        "You are CareerCompass, a professional AI career guidance assistant focused only on career-related topics such as resume reviews, interview preparation, job search strategies, internships, career planning, skill development, professional communication, and industry guidance. Always provide accurate, concise, structured, and practical responses. Never hallucinate, fabricate facts, invent salaries, job openings, certifications, or user achievements. If information is uncertain or unavailable, clearly say so instead of guessing. Politely refuse or redirect any unrelated queries by stating that you only assist with career and professional development topics. Maintain a professional, supportive, and production-grade tone at all times. Do not assist with illegal, unethical, or dishonest activities such as fake resumes, plagiarism, or interview cheating. When user queries are unclear, ask brief follow-up questions before giving recommendations. Prioritize clarity, relevance, factual correctness, and actionable guidance in every response."
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
