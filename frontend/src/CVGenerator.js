import React, { useState } from "react";
import "./CVGenerator.css";

const EXAMPLES = [
  "Ana smiyti Youssef, drast génie informatique f Université Mohammed V f Rabat, tjrbt 3 snin ka développeur backend f startup. Kant kankhdm b Python w Django.",
  "Ingénieur en génie civil diplômé de l'EHTP en 2019. J'ai travaillé 4 ans chez Bouygues Maroc sur des projets d'infrastructure routière. Je maîtrise AutoCAD et Revit.",
  "Licenciée en marketing digital à l'ISCAE Casablanca. 3 ans d'expérience en agence : réseaux sociaux, SEO, Google Ads. Objectif : responsable marketing.",
  "Master en finance d'entreprise. Un an en contrôle de gestion dans l'agroalimentaire. Certifiée Excel avancé et SAP. Recherche poste analyste financier.",
];

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function CVGenerator() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [cv, setCv] = useState(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  async function generateCV() {
    if (!input.trim()) return;
    setLoading(true);
    setError("");
    setCv(null);

    try {
      const res = await fetch(API_URL + "/api/generate-cv", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: input }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Erreur serveur");
      setCv(data.cv);
    } catch (e) {
      setError(e.message || "Une erreur est survenue.");
    } finally {
      setLoading(false);
    }
  }

  function copyCV() {
    const el = document.getElementById("cv-doc");
    if (!el) return;
    navigator.clipboard.writeText(el.innerText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div className="cv-app">
      <div className="cv-header">
        <div className="cv-logo">Talent<span>Dar</span></div>
        <div className="cv-tagline">CV intelligent — Darija · Français · English</div>
      </div>

      <div className="cv-card">
        <div className="cv-label">Décris ton parcours</div>
        <textarea
          className="cv-textarea"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={"Exemples :\n• Ana drast génie info f Rabat, khdam 3 snin f startup...\n• J'ai une licence en marketing, 5 ans d'expérience en vente...\n• I have a degree in CS and 2 years as a backend developer..."}
          rows={6}
        />
        <div className="cv-chips">
          {["Darija", "Ingénieur", "Marketing", "Finance"].map((label, i) => (
            <button key={i} className="chip" onClick={() => setInput(EXAMPLES[i])}>
              {label}
            </button>
          ))}
        </div>
        {error && <div className="cv-error">{error}</div>}
      </div>

      <button
        className="cv-btn-generate"
        onClick={generateCV}
        disabled={loading || !input.trim()}
      >
        {loading ? "Génération en cours..." : "Générer mon CV professionnel"}
      </button>

      {cv && (
        <div className="cv-wrapper">
          <div className="cv-doc" id="cv-doc">

            <div className="cv-doc-header">
              <div>
                <div className="cv-name">{cv.name}</div>
                <div className="cv-title-line">{cv.title}</div>
              </div>
              <div className="cv-contacts">
                {cv.contact && (
                  <>
                    {cv.contact.email && <div>{cv.contact.email}</div>}
                    {cv.contact.phone && <div>{cv.contact.phone}</div>}
                    {cv.contact.location && <div>{cv.contact.location}</div>}
                    {cv.contact.linkedin && <div>{cv.contact.linkedin}</div>}
                  </>
                )}
              </div>
            </div>

            {cv.summary && (
              <div className="cv-section">
                <div className="cv-section-title">Profil</div>
                <p className="cv-summary">{cv.summary}</p>
              </div>
            )}

            {cv.experience && cv.experience.length > 0 && (
              <div className="cv-section">
                <div className="cv-section-title">Expérience professionnelle</div>
                {cv.experience.map((e, i) => (
                  <div key={i} className="cv-entry">
                    <div className="cv-entry-row">
                      <span className="cv-entry-title">{e.role}</span>
                      <span className="cv-entry-date">{e.period}</span>
                    </div>
                    <div className="cv-entry-company">{e.company}</div>
                    <div className="cv-entry-desc">{e.description}</div>
                  </div>
                ))}
              </div>
            )}

            {cv.education && cv.education.length > 0 && (
              <div className="cv-section">
                <div className="cv-section-title">Formation</div>
                {cv.education.map((e, i) => (
                  <div key={i} className="cv-entry">
                    <div className="cv-entry-row">
                      <span className="cv-entry-title">{e.degree}</span>
                      <span className="cv-entry-date">{e.period}</span>
                    </div>
                    <div className="cv-entry-company">{e.school}</div>
                  </div>
                ))}
              </div>
            )}

            {cv.skills && cv.skills.length > 0 && (
              <div className="cv-section">
                <div className="cv-section-title">Compétences</div>
                <div className="cv-tags">
                  {cv.skills.map((s, i) => <span key={i} className="cv-tag">{s}</span>)}
                </div>
              </div>
            )}

            {cv.languages && cv.languages.length > 0 && (
              <div className="cv-section">
                <div className="cv-section-title">Langues</div>
                <div className="cv-tags">
                  {cv.languages.map((l, i) => <span key={i} className="cv-tag">{l}</span>)}
                </div>
              </div>
            )}
          </div>

          <div className="cv-actions">
            <button className="cv-btn-outline" onClick={() => { setCv(null); setInput(""); }}>
              Nouveau CV
            </button>
            <button className="cv-btn-outline" onClick={copyCV}>
              {copied ? "Copié !" : "Copier le texte"}
            </button>
            <button className="cv-btn-outline" onClick={() => window.print()}>
              Imprimer / PDF
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default CVGenerator;