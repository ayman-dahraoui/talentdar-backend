import React, { useState } from "react";
import CVGenerator from "./CVGenerator";
import MicroMissions from "./MicroMissions";
import "./App.css";

function App() {
  const [page, setPage] = useState("cv");

  const getNavBtnClass = (btnPage) => {
    return page === btnPage ? "nav-btn active" : "nav-btn";
  };

  return (
    <div className="app-container">
      <nav className="nav">
        <div className="nav-logo">
          Talent<span>Dar</span>
        </div>
        <div className="nav-links">
          <button
            className={getNavBtnClass("cv")}
            onClick={() => setPage("cv")}
            aria-pressed={page === "cv"}
          >
            CV Intelligent
          </button>
          <button
            className={getNavBtnClass("missions")}
            onClick={() => setPage("missions")}
            aria-pressed={page === "missions"}
          >
            Micro-missions
          </button>
        </div>
      </nav>

      <main className="content">
        {page === "cv" ? <CVGenerator /> : <MicroMissions />}
      </main>
    </div>
  );
}

export default App;