import React, { useState, useEffect, useCallback } from "react";
import "./MicroMissions.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const DOMAINS = [
  { key: "all", label: "Toutes" },
  { key: "dev", label: "Développement" },
  { key: "design", label: "Design" },
  { key: "marketing", label: "Marketing" },
  { key: "data", label: "Data" },
  { key: "gestion", label: "Gestion" },
];

function MicroMissions() {
  const [missions, setMissions] = useState([]);
  const [filter, setFilter] = useState("all");
  const [completed, setCompleted] = useState(new Set());
  const [openDetail, setOpenDetail] = useState(null);
  const [totalXP, setTotalXP] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showGenForm, setShowGenForm] = useState(false);
  const [genProfile, setGenProfile] = useState("");
  const [genDomain, setGenDomain] = useState("");
  const [genLoading, setGenLoading] = useState(false);
  const [generatedMission, setGeneratedMission] = useState(null);

  const fetchMissions = useCallback(async () => {
    setLoading(true);
    try {
      const url = filter === "all"
        ? API_URL + "/api/missions"
        : `${API_URL}/api/missions?domain=${filter}`;
      const res = await fetch(url);
      const data = await res.json();
      setMissions(data);
    } catch {
      setMissions([]);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchMissions();
  }, [fetchMissions]);

  function toggleComplete(mission) {
    const newSet = new Set(completed);
    if (newSet.has(mission.id)) {
      newSet.delete(mission.id);
      setTotalXP(function(prev) { return prev - mission.xp; });
    } else {
      newSet.add(mission.id);
      setTotalXP(function(prev) { return prev + mission.xp; });
    }
    setCompleted(newSet);
  }

  async function generatePersonalized() {
    if (!genProfile.trim()) return;
    setGenLoading(true);
    setGeneratedMission(null);
    try {
      const res = await fetch(API_URL + "/api/missions/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile: genProfile, domain: genDomain }),
      });
      const data = await res.json();
      if (data.success) setGeneratedMission(data.mission);
    } catch {
      alert("Erreur lors de la génération.");
    } finally {
      setGenLoading(false);
    }
  }

  const portfolio = Array.from(completed)
    .map(function(id) {
      return missions.find(function(m) { return m.id === id; }) ||
        (generatedMission && generatedMission.id === id ? generatedMission : null);
    })
    .filter(Boolean);

  return (
    <div className="mm-app">
      <div className="mm-header">
        <div className="mm-logo">Talent<span>Dar</span></div>
        <div className="mm-tagline">Micro-missions — construis ton portfolio avant d'être recruté</div>
      </div>

      <div className="mm-stats">
        <div className="mm-stat">
          <div className="mm-stat-val">{missions.length}</div>
          <div className="mm-stat-lbl">Disponibles</div>
        </div>
        <div className="mm-stat">
          <div className="mm-stat-val green">{completed.size}</div>
          <div className="mm-stat-lbl">Complétées</div>
        </div>
        <div className="mm-stat">
          <div className="mm-stat-val">{totalXP} XP</div>
          <div className="mm-stat-lbl">Points gagnés</div>
        </div>
      </div>

      <div className="mm-filters">
        {DOMAINS.map(function(d) {
          return (
            <button
              key={d.key}
              className={"mm-flt" + (filter === d.key ? " active" : "")}
              onClick={function() { setFilter(d.key); }}
            >
              {d.label}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="mm-loading">Chargement...</div>
      ) : (
        <div className="mm-list">
          {missions.map(function(m) {
            return (
              <MissionCard
                key={m.id}
                mission={m}
                done={completed.has(m.id)}
                open={openDetail === m.id}
                onToggleComplete={function() { toggleComplete(m); }}
                onToggleDetail={function() { setOpenDetail(openDetail === m.id ? null : m.id); }}
              />
            );
          })}
        </div>
      )}

      <div className="mm-gen-section">
        <button className="mm-gen-toggle" onClick={function() { setShowGenForm(!showGenForm); }}>
          {showGenForm ? "Masquer" : "Générer une mission personnalisée avec l'IA"}
        </button>

        {showGenForm && (
          <div className="mm-gen-form">
            <textarea
              className="mm-textarea"
              value={genProfile}
              onChange={function(e) { setGenProfile(e.target.value); }}
              placeholder="Décris ton profil : niveau, compétences, objectif... (darija ou français)"
              rows={3}
            />
            <select
              className="mm-select"
              value={genDomain}
              onChange={function(e) { setGenDomain(e.target.value); }}
            >
              <option value="">Tous les domaines</option>
              <option value="dev">Développement</option>
              <option value="design">Design</option>
              <option value="marketing">Marketing</option>
              <option value="data">Data</option>
              <option value="gestion">Gestion</option>
            </select>
            <button
              className="mm-btn-gen"
              onClick={generatePersonalized}
              disabled={genLoading || !genProfile.trim()}
            >
              {genLoading ? "Génération..." : "Générer ma mission"}
            </button>
            {generatedMission && (
              <MissionCard
                mission={generatedMission}
                done={completed.has(generatedMission.id)}
                open={openDetail === generatedMission.id}
                onToggleComplete={function() { toggleComplete(generatedMission); }}
                onToggleDetail={function() { setOpenDetail(openDetail === generatedMission.id ? null : generatedMission.id); }}
                isGenerated={true}
              />
            )}
          </div>
        )}
      </div>

      <div className="mm-portfolio">
        <div className="mm-section-title">Mon portfolio</div>
        {portfolio.length === 0 ? (
          <div className="mm-empty">Complète des missions pour construire ton portfolio</div>
        ) : (
          <div className="mm-port-list">
            {portfolio.map(function(m) {
              return (
                <div key={m.id} className="mm-port-item">
                  <span className="mm-port-name">{m.title}</span>
                  <span className="mm-port-meta">{m.domainLabel} · +{m.xp} XP</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function MissionCard(props) {
  var m = props.mission;
  var done = props.done;
  var open = props.open;
  var isGenerated = props.isGenerated;

  return (
    <div className={"mm-card" + (done ? " done" : "") + (isGenerated ? " generated" : "")}>
      <div className="mm-card-top">
        <div className="mm-card-left">
          <div className="mm-badges">
            <span className="badge domain">{m.domainLabel}</span>
            <span className={"badge diff-" + m.difficulty}>{m.diffLabel}</span>
            {isGenerated && <span className="badge gen">IA personnalisée</span>}
          </div>
          <div className="mm-card-title">{m.title}</div>
          <div className="mm-card-desc">{m.desc}</div>
        </div>
        <div className="mm-card-right">
          <span className="mm-xp">+{m.xp} XP</span>
          <button
            className={done ? "btn-undo" : "btn-start"}
            onClick={props.onToggleComplete}
          >
            {done ? "Annuler" : "Commencer"}
          </button>
        </div>
      </div>

      <div className="mm-card-footer">
        <span className="mm-time">{m.time}</span>
        <div className="mm-progress">
          <div className="mm-progress-fill" style={{ width: done ? "100%" : "0%" }} />
        </div>
        <button className="btn-detail" onClick={props.onToggleDetail}>
          {open ? "Masquer ▲" : "Détails ▼"}
        </button>
      </div>

      {open && (
        <div className="mm-detail">
          <ul className="mm-steps">
            {m.steps.map(function(s, i) { return <li key={i}>{s}</li>; })}
          </ul>
          <div className="mm-deliverable">Livrable : {m.deliverable}</div>
        </div>
      )}
    </div>
  );
}

export default MicroMissions;