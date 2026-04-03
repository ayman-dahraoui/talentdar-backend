from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pymongo import MongoClient
import google.generativeai as genai
import json
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="TalentDar API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(os.getenv("MONGODB_URL"))
db = client["talentdar1"]




@app.get("/")
def root():
    return {"message": "TalentDar API"}


@app.get("/health")
def health():
    try:
        client.admin.command("ping")
        return {"status": "ok", "mongodb": "connecté ✅"}
    except Exception as e:
        return {"status": "error", "mongodb": str(e)}



@app.post("/api/generate-cv")
async def generate_cv(data: dict):
    description = data.get("description", "").strip()
    if not description:
        raise HTTPException(status_code=400, detail="Description vide.")

    prompt = f"""Tu es un expert RH marocain.
Génère un CV en JSON uniquement.

{{
  "name": "Prénom Nom",
  "title": "Titre professionnel",
  "contact": {{
    "email": "email@exemple.com",
    "phone": "+212",
    "location": "Maroc",
    "linkedin": ""
  }},
  "summary": "",
  "experience": [],
  "education": [],
  "skills": [],
  "languages": []
}}

Description : {description}"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        raw = response.text.strip().replace("```json", "").replace("```", "").strip()
        cv_data = json.loads(raw)
        return {"success": True, "cv": cv_data}
    except:
        raise HTTPException(status_code=500, detail="Erreur génération CV.")




MISSIONS = [
    {
        "id": 1,
        "domain": "dev",
        "title": "Landing page startup",
        "desc": "Créer une landing page responsive",
        "difficulty": "easy",
        "xp": 150
    }
]


@app.get("/api/missions")
def get_missions():
    return MISSIONS