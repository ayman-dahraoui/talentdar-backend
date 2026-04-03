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
    return {"message": "Hello World"}
 
 
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
 
    prompt = f"""Tu es un expert RH et rédacteur de CV professionnel marocain.
L'utilisateur va te décrire son parcours en darija, français ou anglais.
 
Tu dois générer un CV structuré et professionnel en JSON avec cette structure exacte.
Réponds UNIQUEMENT avec le JSON brut, sans texte avant ou après, sans backticks markdown.
 
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
    {{
      "role": "Titre du poste",
      "company": "Entreprise",
      "period": "2021 – 2024",
      "description": "Description des responsabilités et réalisations"
    }}
  ],
  "education": [
    {{
      "degree": "Diplôme",
      "school": "École / Université",
      "period": "2017 – 2021"
    }}
  ],
  "skills": ["Compétence 1", "Compétence 2", "Compétence 3"],
  "languages": ["Arabe (natif)", "Français (courant)", "Anglais (professionnel)"]
}}
 
Si des informations manquent, génère des données plausibles et cohérentes.
Le CV doit être rédigé en français professionnel, même si la description est en darija.
 
Description du parcours : {description}"""
 
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
 
        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        cv_data = json.loads(raw)
 
        return {"success": True, "cv": cv_data}
 
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur parsing JSON depuis l'IA.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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




MISSIONS = [
    {
        "id": 1, "domain": "dev", "domainLabel": "Développement",
        "title": "Landing page pour une startup fictive",
        "desc": "Crée une page web responsive pour une startup marocaine de ton choix avec HTML, CSS et JS.",
        "difficulty": "easy", "diffLabel": "Débutant", "xp": 150, "time": "3-5h",
        "steps": [
            "Choisir un concept de startup (ex: livraison de repas à Rabat)",
            "Créer la structure HTML avec header, hero, features, footer",
            "Styliser avec CSS responsive (mobile first)",
            "Ajouter une interaction JS simple (formulaire ou animation)"
        ],
        "deliverable": "Fichier index.html hébergé sur GitHub Pages"
    },
    {
        "id": 2, "domain": "dev", "domainLabel": "Développement",
        "title": "API REST avec FastAPI — gestion de tâches",
        "desc": "Développe une mini API de gestion de tâches (TODO) avec FastAPI et SQLite.",
        "difficulty": "med", "diffLabel": "Intermédiaire", "xp": 250, "time": "5-8h",
        "steps": [
            "Installer FastAPI et SQLite",
            "Créer les modèles (Task: id, title, status, date)",
            "Implémenter les endpoints CRUD (GET, POST, PUT, DELETE)",
            "Tester avec Swagger UI et documenter"
        ],
        "deliverable": "Repo GitHub avec README et captures Swagger"
    },
    {
        "id": 3, "domain": "design", "domainLabel": "Design",
        "title": "Redesign d'une app marocaine",
        "desc": "Choisis une app marocaine et propose un redesign moderne de ses 3 écrans principaux.",
        "difficulty": "med", "diffLabel": "Intermédiaire", "xp": 200, "time": "4-6h",
        "steps": [
            "Analyser l'app existante (problèmes UX)",
            "Créer des wireframes sur Figma",
            "Concevoir 3 écrans HD avec une charte graphique cohérente",
            "Rédiger un court brief design (1 page)"
        ],
        "deliverable": "Fichier Figma ou PDF avec les 3 écrans + brief"
    },
    {
        "id": 4, "domain": "marketing", "domainLabel": "Marketing",
        "title": "Stratégie réseaux sociaux pour une PME",
        "desc": "Crée un plan de contenu d'un mois pour une PME marocaine fictive avec calendrier éditorial.",
        "difficulty": "easy", "diffLabel": "Débutant", "xp": 120, "time": "2-4h",
        "steps": [
            "Définir la persona cible et le ton de la marque",
            "Créer un calendrier éditorial (4 semaines, 3 posts/semaine)",
            "Rédiger 5 exemples de posts avec visuels (Canva)",
            "Proposer 3 KPIs à suivre"
        ],
        "deliverable": "PDF avec calendrier + 5 posts prêts à publier"
    },
    {
        "id": 5, "domain": "data", "domainLabel": "Data",
        "title": "Analyse des prix immobiliers à Casablanca",
        "desc": "Collecte et analyse des données immobilières publiques pour produire un rapport avec visualisations.",
        "difficulty": "hard", "diffLabel": "Avancé", "xp": 350, "time": "8-12h",
        "steps": [
            "Scraper ou collecter des données d'annonces immobilières",
            "Nettoyer les données avec Python/Pandas",
            "Créer des visualisations (prix/m², par quartier, tendance)",
            "Rédiger un rapport d'analyse de 2 pages"
        ],
        "deliverable": "Notebook Jupyter + rapport PDF + visualisations"
    },
    {
        "id": 6, "domain": "gestion", "domainLabel": "Gestion",
        "title": "Business plan d'un projet entrepreneurial",
        "desc": "Rédige un business plan complet pour une idée de startup marocaine avec étude de marché.",
        "difficulty": "hard", "diffLabel": "Avancé", "xp": 300, "time": "6-10h",
        "steps": [
            "Définir l'idée, la proposition de valeur et le marché cible",
            "Analyser la concurrence (3-5 acteurs)",
            "Construire un modèle financier simple (3 ans)",
            "Rédiger le business plan (10-15 pages)"
        ],
        "deliverable": "Business plan complet en PDF"
    },
    {
        "id": 7, "domain": "design", "domainLabel": "Design",
        "title": "Logo et identité visuelle complète",
        "desc": "Crée une identité visuelle pour une marque fictive marocaine : logo, couleurs, typographie.",
        "difficulty": "med", "diffLabel": "Intermédiaire", "xp": 180, "time": "4-6h",
        "steps": [
            "Définir les valeurs et la personnalité de la marque",
            "Créer le logo en plusieurs variantes",
            "Définir la palette de couleurs et les typographies",
            "Produire un mini brand book (3-5 pages)"
        ],
        "deliverable": "SVG/PNG du logo + PDF brand book"
    },
    {
        "id": 8, "domain": "marketing", "domainLabel": "Marketing",
        "title": "Campagne email marketing de A à Z",
        "desc": "Conçois une séquence de 5 emails d'onboarding pour un produit SaaS marocain fictif.",
        "difficulty": "easy", "diffLabel": "Débutant", "xp": 130, "time": "3-5h",
        "steps": [
            "Définir le parcours utilisateur et les objectifs de chaque email",
            "Rédiger les 5 emails (sujet, corps, CTA)",
            "Créer les visuels avec Canva",
            "Simuler les métriques attendues"
        ],
        "deliverable": "Document avec les 5 emails complets + visuels"
    }
]




@app.get("/")
def root():
    return {"message": "TalentDar API"}


@app.get("/health")
def health():
    return {"status": "ok"}




@app.post("/api/generate-cv")
async def generate_cv(data: dict):
    description = data.get("description", "").strip()
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
  "skills": ["Compétence 1", "Compétence 2"],
  "languages": ["Arabe (natif)", "Français (courant)"]
}}

Description : {description}"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        raw = response.text.strip().replace("```json", "").replace("```", "").strip()
        cv_data = json.loads(raw)
        return {"success": True, "cv": cv_data}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur parsing JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/api/missions")
def get_missions(domain: str = None):
    """Retourne toutes les missions, filtrées par domaine si précisé."""
    if domain and domain != "all":
        return [m for m in MISSIONS if m["domain"] == domain]
    return MISSIONS


@app.get("/api/missions/{mission_id}")
def get_mission(mission_id: int):
    """Retourne le détail d'une mission par son ID."""
    mission = next((m for m in MISSIONS if m["id"] == mission_id), None)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission introuvable.")
    return mission


@app.post("/api/missions/generate")
async def generate_mission(data: dict):
    """Génère une mission personnalisée selon le profil avec Gemini."""
    profile = data.get("profile", "").strip()
    domain = data.get("domain", "").strip()

    if not profile:
        raise HTTPException(status_code=400, detail="Profil vide.")

    prompt = f"""Tu es un expert en développement de carrière pour les jeunes marocains.
Génère une micro-mission concrète et réalisable pour construire un portfolio.

Profil : {profile}
Domaine souhaité : {domain or 'libre'}

Réponds UNIQUEMENT avec ce JSON brut, sans texte ni backticks :

{{
  "title": "Titre court et accrocheur",
  "desc": "Description claire en 1-2 phrases",
  "difficulty": "easy",
  "diffLabel": "Débutant",
  "xp": 150,
  "time": "3-5h",
  "steps": ["Étape 1", "Étape 2", "Étape 3", "Étape 4"],
  "deliverable": "Description précise du livrable attendu",
  "domain": "{domain or 'général'}",
  "domainLabel": "Nom du domaine"
}}"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        raw = response.text.strip().replace("```json", "").replace("```", "").strip()
        mission = json.loads(raw)
        mission["id"] = 999
        return {"success": True, "mission": mission}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur parsing JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))