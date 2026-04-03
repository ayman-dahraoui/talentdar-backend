from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
from groq import Groq
import certifi
import ssl
import json
import re
import os

load_dotenv()

# ── Config ───────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MONGODB_URL  = os.getenv("MONGODB_URL")

if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY manquante dans .env")
if not MONGODB_URL:
    raise EnvironmentError("MONGODB_URL manquante dans .env")

# ── Groq ─────────────────────────────────────────────────────────────────────
groq_client = Groq(api_key=GROQ_API_KEY)

# ── MongoDB — fix SSL Windows ─────────────────────────────────────────────────
# Le problème TLSV1_ALERT_INTERNAL_ERROR vient du contexte SSL de Python sur
# Windows qui n'accepte pas les certificats d'Atlas par défaut.
# Solution : forcer le contexte SSL avec certifi + désactiver la vérification
# du nom d'hôte (uniquement en dev local — pas en production).

ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE   # ← fix principal pour Windows

mongo_client = MongoClient(
    MONGODB_URL,
    tls=True,
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=True,   # ← nécessaire sur certains Windows
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=30000,
    socketTimeoutMS=30000,
)

db            = mongo_client["talentdar1"]
cv_collection = db["cvs"]

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="TalentDar API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schémas Pydantic ──────────────────────────────────────────────────────────
class CVRequest(BaseModel):
    description: str

class MissionRequest(BaseModel):
    profile: str
    domain: Optional[str] = None

# ── Helper JSON ───────────────────────────────────────────────────────────────
def parse_json_text(raw: str) -> dict:
    cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
    match   = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if not match:
        raise ValueError("Aucun JSON valide trouvé dans la réponse IA")
    return json.loads(match.group(0))

# ── Missions statiques ────────────────────────────────────────────────────────
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

# ── Routes de base ────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "TalentDar API — Groq + MongoDB"}


@app.get("/health")
def health():
    try:
        mongo_client.admin.command("ping")
        mongo_ok = "connecté"
    except Exception as e:
        mongo_ok = f"erreur: {str(e)[:80]}"

    try:
        groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1
        )
        groq_ok = "connecté"
    except Exception as e:
        groq_ok = f"erreur: {str(e)[:80]}"

    return {"status": "ok", "mongodb": mongo_ok, "groq": groq_ok}


# ── CV Intelligent ────────────────────────────────────────────────────────────
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
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000,
        )
        cv_data = parse_json_text(completion.choices[0].message.content)

        # Sauvegarder dans MongoDB (sans bloquer si erreur)
        try:
            cv_collection.insert_one({**cv_data, "description_originale": description})
        except Exception:
            pass

        return {"success": True, "cv": cv_data}

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cvs")
def get_all_cvs():
    """Retourne tous les CVs sauvegardés dans MongoDB."""
    try:
        cvs = list(cv_collection.find({}, {"_id": 0}))
        return cvs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Micro-missions ────────────────────────────────────────────────────────────
@app.get("/api/missions")
def get_missions(
    domain: Optional[str] = Query("all", description="dev / design / marketing / data / gestion / all")
):
    if domain and domain.lower() != "all":
        return [m for m in MISSIONS if m["domain"].lower() == domain.lower()]
    return MISSIONS


@app.get("/api/missions/{mission_id}")
def get_mission(mission_id: int):
    mission = next((m for m in MISSIONS if m["id"] == mission_id), None)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission introuvable.")
    return mission


@app.post("/api/missions/generate")
async def generate_mission(data: MissionRequest):
    profile = data.profile.strip()
    domain  = (data.domain or "").strip()
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
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1500,
        )
        mission = parse_json_text(completion.choices[0].message.content)
        mission["id"] = 999
        return {"success": True, "mission": mission}

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Coach Entretien ───────────────────────────────────────

class EntretienSetup(BaseModel):
    poste: str
    secteur: str
    niveau: str
    lang: Optional[str] = "fr"

class EntretienEval(BaseModel):
    poste: str
    niveau: str
    question: str
    reponse: str
    lang: Optional[str] = "fr"

class EntretienFinal(BaseModel):
    poste: str
    niveau: str
    questions: list
    reponses: list
    scores: list


@app.post("/api/entretien/questions")
async def generate_questions(data: EntretienSetup):
    poste = data.poste.strip()
    if not poste:
        raise HTTPException(status_code=400, detail="Poste vide.")

    if data.lang == "darija":
        langue = "Les questions doivent être en darija marocain."
    elif data.lang == "mix":
        langue = "Alterne entre français et darija marocain."
    else:
        langue = "Les questions doivent être en français professionnel."

    prompt = f"""Tu es un recruteur RH expert marocain.
Génère exactement 5 questions d'entretien pour ce profil.

Poste : {poste}
Secteur : {data.secteur}
Niveau : {data.niveau}
{langue}

Mélange questions comportementales et techniques liées au poste.

Réponds UNIQUEMENT avec ce JSON brut, sans texte ni backticks :

{{"questions": ["Question 1","Question 2","Question 3","Question 4","Question 5"]}}"""

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=800,
        )
        result = parse_json_text(completion.choices[0].message.content)
        return {"success": True, "questions": result.get("questions", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/entretien/evaluer")
async def evaluer_reponse(data: EntretienEval):
    if not data.reponse.strip():
        raise HTTPException(status_code=400, detail="Réponse vide.")

    langue_fb = "en darija marocain" if data.lang == "darija" else "en français professionnel"

    prompt = f"""Tu es un recruteur RH expert marocain. Évalue cette réponse d'entretien.

Poste visé : {data.poste}
Niveau : {data.niveau}
Question : {data.question}
Réponse du candidat : {data.reponse}

Donne le feedback {langue_fb}.

Réponds UNIQUEMENT avec ce JSON brut, sans texte ni backticks :

{{
  "score": 7,
  "note_globale": "Bien",
  "points_forts": ["Point fort 1", "Point fort 2"],
  "points_ameliorer": ["Point à améliorer 1"],
  "conseil": "Conseil court et actionnable en 1-2 phrases.",
  "exemple_meilleure_reponse": "Reformulation plus impactante de la réponse."
}}"""

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800,
        )
        feedback = parse_json_text(completion.choices[0].message.content)

        try:
            db["entretiens"].insert_one({
                "poste": data.poste, "niveau": data.niveau,
                "question": data.question, "reponse": data.reponse,
                "feedback": feedback, "lang": data.lang
            })
        except Exception:
            pass

        return {"success": True, "feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/entretien/rapport")
async def generer_rapport(data: EntretienFinal):
    if not data.reponses:
        raise HTTPException(status_code=400, detail="Aucune réponse.")

    avg = sum(data.scores) / len(data.scores) if data.scores else 0
    qa  = "\n".join([
        f"Q{i+1}: {data.questions[i]}\nR: {data.reponses[i]}"
        for i in range(min(len(data.questions), len(data.reponses)))
    ])

    prompt = f"""Tu es un coach carrière expert marocain.
Génère un rapport de bilan d'entretien.

Poste : {data.poste} | Niveau : {data.niveau} | Score moyen : {avg:.1f}/10

{qa}

Réponds UNIQUEMENT avec ce JSON brut, sans texte ni backticks :

{{
  "score_global": {avg:.1f},
  "mention": "Excellent",
  "resume": "Résumé global en 2-3 phrases.",
  "points_forts": ["Force 1", "Force 2", "Force 3"],
  "axes_amelioration": ["Axe 1", "Axe 2"],
  "conseils_pratiques": ["Conseil 1", "Conseil 2", "Conseil 3"],
  "prochaines_etapes": "Ce que le candidat doit faire concrètement."
}}"""

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
        )
        rapport = parse_json_text(completion.choices[0].message.content)
        return {"success": True, "rapport": rapport}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))