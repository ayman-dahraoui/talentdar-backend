from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
import google.generativeai as genai
import json
import os

load_dotenv()

# ── Config ──────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGODB_URL = os.getenv("MONGODB_URL")

if not GEMINI_API_KEY:
    raise EnvironmentError("La variable d'environnement GEMINI_API_KEY est requise.")
if not MONGODB_URL:
    raise EnvironmentError("La variable d'environnement MONGODB_URL est requise.")

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    raise RuntimeError(f"Impossible de configurer le client Gemini AI : {e}")

mongo_client = MongoClient(MONGODB_URL)
db = mongo_client["talentdar1"]
cv_collection = db["cvs"]

app = FastAPI(title="TalentDar API", version="1.0.0")

class CVRequest(BaseModel):
    description: str

class MissionRequest(BaseModel):
    profile: str
    domain: Optional[str] = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Missions statiques ───────────────────
MISSIONS = [
    {
        "id": 1, "domain": "dev", "domainLabel": "Développement",
        "title": "Landing page pour une startup fictive",
        "desc": "Crée une page web responsive pour une startup marocaine avec HTML, CSS et JS.",
        "difficulty": "easy", "diffLabel": "Débutant", "xp": 150, "time": "3-5h",
        "steps": [
            "Choisir un concept de startup (ex: livraison de repas à Rabat)",
            "Créer la structure HTML avec header, hero, features, footer",
            "Styliser avec CSS responsive (mobile first)",
            "Ajouter une interaction JS simple"
        ],
        "deliverable": "Fichier index.html hébergé sur GitHub Pages"
    },
    {
        "id": 2, "domain": "dev", "domainLabel": "Développement",
        "title": "API REST avec FastAPI — gestion de tâches",
        "desc": "Développe une mini API TODO avec FastAPI et SQLite.",
        "difficulty": "med", "diffLabel": "Intermédiaire", "xp": 250, "time": "5-8h",
        "steps": [
            "Installer FastAPI et SQLite",
            "Créer les modèles (Task: id, title, status, date)",
            "Implémenter les endpoints CRUD",
            "Tester avec Swagger UI"
        ],
        "deliverable": "Repo GitHub avec README et captures Swagger"
    },
    {
        "id": 3, "domain": "design", "domainLabel": "Design",
        "title": "Redesign d'une app marocaine",
        "desc": "Propose un redesign moderne de 3 écrans d'une app marocaine existante.",
        "difficulty": "med", "diffLabel": "Intermédiaire", "xp": 200, "time": "4-6h",
        "steps": [
            "Analyser l'app existante (problèmes UX)",
            "Créer des wireframes sur Figma",
            "Concevoir 3 écrans HD avec charte graphique",
            "Rédiger un brief design (1 page)"
        ],
        "deliverable": "Fichier Figma ou PDF avec les 3 écrans + brief"
    },
    {
        "id": 4, "domain": "marketing", "domainLabel": "Marketing",
        "title": "Stratégie réseaux sociaux pour une PME",
        "desc": "Crée un plan de contenu d'un mois pour une PME marocaine fictive.",
        "difficulty": "easy", "diffLabel": "Débutant", "xp": 120, "time": "2-4h",
        "steps": [
            "Définir la persona cible et le ton de la marque",
            "Créer un calendrier éditorial (4 semaines)",
            "Rédiger 5 exemples de posts avec visuels",
            "Proposer 3 KPIs à suivre"
        ],
        "deliverable": "PDF avec calendrier + 5 posts prêts à publier"
    },
    {
        "id": 5, "domain": "data", "domainLabel": "Data",
        "title": "Analyse des prix immobiliers à Casablanca",
        "desc": "Collecte et analyse des données immobilières pour produire un rapport.",
        "difficulty": "hard", "diffLabel": "Avancé", "xp": 350, "time": "8-12h",
        "steps": [
            "Collecter des données d'annonces immobilières",
            "Nettoyer les données avec Python/Pandas",
            "Créer des visualisations (prix/m², par quartier)",
            "Rédiger un rapport d'analyse de 2 pages"
        ],
        "deliverable": "Notebook Jupyter + rapport PDF + visualisations"
    },
    {
        "id": 6, "domain": "gestion", "domainLabel": "Gestion",
        "title": "Business plan d'un projet entrepreneurial",
        "desc": "Rédige un business plan complet pour une startup marocaine.",
        "difficulty": "hard", "diffLabel": "Avancé", "xp": 300, "time": "6-10h",
        "steps": [
            "Définir l'idée et la proposition de valeur",
            "Analyser la concurrence (3-5 acteurs)",
            "Construire un modèle financier simple (3 ans)",
            "Rédiger le business plan (10-15 pages)"
        ],
        "deliverable": "Business plan complet en PDF"
    },
    {
        "id": 7, "domain": "design", "domainLabel": "Design",
        "title": "Logo et identité visuelle complète",
        "desc": "Crée une identité visuelle pour une marque fictive marocaine.",
        "difficulty": "med", "diffLabel": "Intermédiaire", "xp": 180, "time": "4-6h",
        "steps": [
            "Définir les valeurs et la personnalité de la marque",
            "Créer le logo en plusieurs variantes",
            "Définir la palette de couleurs et typographies",
            "Produire un mini brand book (3-5 pages)"
        ],
        "deliverable": "SVG/PNG du logo + PDF brand book"
    },
    {
        "id": 8, "domain": "marketing", "domainLabel": "Marketing",
        "title": "Campagne email marketing de A à Z",
        "desc": "Conçois une séquence de 5 emails d'onboarding pour un SaaS fictif.",
        "difficulty": "easy", "diffLabel": "Débutant", "xp": 130, "time": "3-5h",
        "steps": [
            "Définir le parcours utilisateur et objectifs",
            "Rédiger les 5 emails (sujet, corps, CTA)",
            "Créer les visuels avec Canva",
            "Simuler les métriques attendues"
        ],
        "deliverable": "Document avec les 5 emails complets + visuels"
    }
]


# ── Routes de base ───────────────────────

@app.get("/")
def root():
    return {"message": "TalentDar API"}


@app.get("/health")
def health():
    try:
        mongo_client.admin.command("ping")
        return {"status": "ok", "mongodb": "connecté"}
    except Exception as e:
        return {"status": "error", "mongodb": str(e)}

def parse_json_text(raw_text: str):
    cleaned = raw_text.strip().replace("```json", "").replace("```", "").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise json.JSONDecodeError("Aucun objet JSON détecté", cleaned, 0)
    return json.loads(cleaned[start : end + 1])

# ── CV Intelligent ───────────────────────

@app.post("/api/generate-cv")
async def generate_cv(data: CVRequest):
    description = data.description.strip()
    if not description:
        raise HTTPException(status_code=400, detail="Description vide.")

    prompt = f"""Tu es un expert RH et rédacteur de CV professionnel marocain.
L'utilisateur décrit son parcours en darija, français ou anglais.

Réponds UNIQUEMENT avec ce JSON brut, sans texte ni backticks :

{{
  "name": "Prénom Nom",
  "title": "Titre professionnel visé",
  "contact": {{
    "email": "email@exemple.com",
    "phone": "+212 6XX XXX XXX",
    "location": "Ville, Maroc",
    "linkedin": "linkedin.com/in/prenom-nom"
  }},
  "summary": "Résumé professionnel percutant de 2-3 phrases",
  "experience": [
    {{"role": "Titre du poste", "company": "Entreprise", "period": "2021 – 2024", "description": "Responsabilités et réalisations"}}
  ],
  "education": [
    {{"degree": "Diplôme", "school": "École / Université", "period": "2017 – 2021"}}
  ],
  "skills": ["Compétence 1", "Compétence 2", "Compétence 3"],
  "languages": ["Arabe (natif)", "Français (courant)", "Anglais (professionnel)"]
}}

Si des informations manquent, génère des données plausibles.
Le CV doit être en français professionnel même si la description est en darija.

Description : {description}"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        cv_data = parse_json_text(response.text)

        # Sauvegarder dans MongoDB
        cv_collection.insert_one({**cv_data, "description_originale": description})

        return {"success": True, "cv": cv_data}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur parsing JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cvs")
def get_all_cvs():
    """Retourne tous les CVs sauvegardés dans MongoDB."""
    cvs = list(cv_collection.find({}, {"_id": 0}))
    return cvs


# ── Micro-missions ───────────────────────

@app.get("/api/missions")
def get_missions(domain: Optional[str] = Query("all", description="Filtrer par domaine: dev/design/marketing/data/gestion/all")):
    if domain and domain.lower() != "all":
        filtered = [m for m in MISSIONS if m.get("domain", "").lower() == domain.lower()]
        return filtered
    return MISSIONS


@app.get("/api/missions/{mission_id}")
def get_mission(mission_id: int):
    mission = next(
        (m for m in MISSIONS if int(m.get("id", -1)) == mission_id),
        None,
    )
    if not mission:
        raise HTTPException(status_code=404, detail="Mission introuvable.")
    return mission


@app.post("/api/missions/generate")
async def generate_mission(data: MissionRequest):
    profile = data.profile.strip()
    domain = (data.domain or "").strip()
    if not profile:
        raise HTTPException(status_code=400, detail="Profil vide.")

    prompt = f"""Tu es un expert en développement de carrière pour les jeunes marocains.
Génère une micro-mission concrète et réalisable pour construire un portfolio.

Profil : {profile}
Domaine : {domain or 'libre'}

Réponds UNIQUEMENT avec ce JSON brut, sans texte ni backticks :

{{
  "title": "Titre court et accrocheur",
  "desc": "Description claire en 1-2 phrases",
  "difficulty": "easy",
  "diffLabel": "Débutant",
  "xp": 150,
  "time": "3-5h",
  "steps": ["Étape 1", "Étape 2", "Étape 3", "Étape 4"],
  "deliverable": "Description du livrable attendu",
  "domain": "{domain or 'général'}",
  "domainLabel": "Nom du domaine"
}}"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        mission = parse_json_text(response.text)
        mission["id"] = 999
        return {"success": True, "mission": mission}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur parsing JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))