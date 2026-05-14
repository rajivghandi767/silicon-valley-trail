// frontend/src/App.tsx
import { useState, useEffect } from "react";
import { apiFetch } from "./utils/api";
import { GameState, GameAction } from "./types";
import { ProjectSwitcher } from "./components/ProjectSwitcher";
import { ReportModal } from "./components/ReportModal";
import { WARNING_THRESHOLDS } from "./constants";
import "./index.css";

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [narrative, setNarrative] = useState<string>(
    "// Establishing secure connection...",
  );

  useEffect(() => {
    apiFetch<GameState>("/api/state/")
      .then((data) => {
        setGameState(data);
        if (data.message) setNarrative(data.message);
      })
      .catch((err: Error) => {
        setError(err.message);
      });
  }, []);

  const handleAction = async (actionType: GameAction) => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await apiFetch<GameState>("/api/action/", {
        method: "POST",
        body: { action: actionType },
      });

      setGameState(data);
      if (data.message) setNarrative(data.message);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRestart = async (force = false) => {
    if (
      !force &&
      !window.confirm(
        "Are you sure you want to restart the game? All progress will be lost.",
      )
    )
      return;

    setIsLoading(true);
    setError(null);
    try {
      const data = await apiFetch<GameState>("/api/restart/", {
        method: "POST",
      });

      setGameState(data);
      if (data.message) setNarrative(data.message);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (error && !gameState)
    return (
      <div style={{ color: "var(--accent-red)", padding: "2rem" }}>
        Error: {error}
      </div>
    );
  if (!gameState) return <div style={{ padding: "2rem" }}>Loading IDE...</div>;

  const isGameOver = gameState.is_won || gameState.is_lost;

  return (
    <div className="app-container">
      <div className="sidebar">
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.75rem",
            paddingBottom: "1.5rem",
            borderBottom: "1px dashed var(--border-color)",
          }}
        >
          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span className="stat-label">Location</span>
            <span
              className="stat-label"
              style={{ opacity: 0.5, fontSize: "0.75rem" }}
            >
              STOP {gameState.sequence_in_journey} OF 10
            </span>
          </div>

          <span
            className="stat-value"
            style={{ color: "var(--accent-orange)", fontSize: "1.15rem" }}
          >
            "{gameState.current_location}"
          </span>
          <span
            style={{
              fontSize: "0.85rem",
              color: "var(--text-main)",
              opacity: 0.8,
              lineHeight: "1.5",
            }}
          >
            {gameState.description}
          </span>
        </div>

        <div className="stat-block">
          <span className="stat-label">
            <span className="hide-on-mobile">Days Remaining</span>
            <span className="show-on-mobile" title="Days Remaining">
              📅
            </span>
          </span>
          <span
            className="stat-value"
            style={{
              color:
                gameState.days_remaining <= WARNING_THRESHOLDS.DAYS
                  ? "var(--accent-red)"
                  : "var(--accent-green)",
            }}
          >
            {gameState.days_remaining}
          </span>
        </div>

        <div className="stat-block">
          <span className="stat-label">
            <span className="hide-on-mobile">Cash</span>
            <span className="show-on-mobile" title="Cash">
              💰
            </span>
          </span>
          <span
            className="stat-value"
            style={{
              color:
                gameState.cash <= WARNING_THRESHOLDS.CASH
                  ? "var(--accent-red)"
                  : "var(--accent-green)",
            }}
          >
            ${gameState.cash.toLocaleString()}
          </span>
        </div>

        <div className="stat-block">
          <span className="stat-label">
            <span className="hide-on-mobile">Award Miles</span>
            <span className="show-on-mobile" title="Award Miles">
              ✈️
            </span>
          </span>
          <span
            className="stat-value"
            style={{
              color:
                gameState.award_miles < WARNING_THRESHOLDS.MILES
                  ? "var(--text-main)"
                  : "var(--accent-blue)",
            }}
          >
            {gameState.award_miles.toLocaleString()}
          </span>
        </div>

        <div className="stat-block">
          <span className="stat-label">
            <span className="hide-on-mobile">Morale</span>
            <span className="show-on-mobile" title="Morale">
              🎭
            </span>
          </span>
          <span
            className="stat-value"
            style={{
              color:
                gameState.morale <= WARNING_THRESHOLDS.MORALE
                  ? "var(--accent-red)"
                  : "var(--accent-green)",
            }}
          >
            {gameState.morale}%
          </span>
        </div>

        <div className="stat-block">
          <span className="stat-label">
            <span className="hide-on-mobile">Bugs</span>
            <span className="show-on-mobile" title="Bugs">
              🐛
            </span>
          </span>
          <span
            className="stat-value"
            style={{
              color:
                gameState.bugs >= WARNING_THRESHOLDS.BUGS_CRITICAL
                  ? "var(--accent-red)"
                  : gameState.bugs >= WARNING_THRESHOLDS.BUGS_WARNING
                    ? "var(--accent-orange)"
                    : "var(--accent-green)",
            }}
          >
            {gameState.bugs} / 50
          </span>
        </div>

        <div
          style={{
            marginTop: "auto",
            paddingTop: "1.5rem",
            borderTop: "1px dashed var(--border-color)",
            fontSize: "0.85rem",
            color: "var(--accent-blue)",
            fontStyle: "italic",
            lineHeight: "1.5",
          }}
        >
          &gt; {gameState.status_summary}
        </div>
      </div>

      <div className="main-window">
        <div className="header">
          <h1 className="title">
            <span className="hide-on-mobile">
              &lt; Silicon Valley Trail: Caribbean Edition /&gt;
            </span>
            <span className="show-on-mobile">&lt; SVT: Caribbean /&gt;</span>
          </h1>
          <div className="header-controls">
            <button
              onClick={() => handleRestart()}
              className="restart-btn"
              title="Restart Game"
            >
              <span className="hide-on-mobile">[ Restart Game ]</span>
              <span className="show-on-mobile">⏮️</span>
            </button>
            <ProjectSwitcher />
          </div>
        </div>

        <div className="game-content">
          <div className="terminal-output">
            {error && (
              <div
                style={{ color: "var(--accent-orange)", marginBottom: "1rem" }}
              >
                // ERROR: {error}
              </div>
            )}
            {narrative}
          </div>

          <div className="button-group">
            <button
              className="action-btn"
              onClick={() => handleAction("code")}
              disabled={isLoading || isGameOver}
            >
              <span className="hide-on-mobile">[ Write Code ]</span>
              <span className="show-on-mobile" title="Write Code">
                💻
              </span>
            </button>
            <button
              className="action-btn"
              onClick={() => handleAction("mentor")}
              disabled={isLoading || isGameOver}
            >
              <span className="hide-on-mobile">[ Mentor ]</span>
              <span className="show-on-mobile" title="Mentor">
                🤝
              </span>
            </button>
            <button
              className="action-btn"
              onClick={() => handleAction("rest")}
              disabled={isLoading || isGameOver}
            >
              <span className="hide-on-mobile">[ Rest ]</span>
              <span className="show-on-mobile" title="Rest">
                🛌
              </span>
            </button>

            <div className="action-separator"></div>

            <button
              className="action-btn fly"
              onClick={() => handleAction("travel_ferry")}
              disabled={isLoading || isGameOver}
            >
              <span className="hide-on-mobile">[ Ferry ]</span>
              <span className="show-on-mobile" title="Ferry">
                ⛴️
              </span>
            </button>
            <button
              className="action-btn fly"
              onClick={() => handleAction("travel_flight")}
              disabled={isLoading || isGameOver}
            >
              <span className="hide-on-mobile">[ Fly ]</span>
              <span className="show-on-mobile" title="Fly">
                ✈️
              </span>
            </button>
          </div>
        </div>

        <div className="footer">
          <span>Built for the LinkedIn REACH Apprenticeship</span>
          <span>
            Developed by{" "}
            <a href="https://rajivwallace.com" target="_blank" rel="noreferrer">
              Rajiv Wallace 🇩🇲
            </a>
          </span>
          <span className="footer-links">
            <a
              href="https://github.com/rajivghandi767"
              target="_blank"
              rel="noreferrer"
            >
              GitHub
            </a>
            <span style={{ margin: "0 0.5rem" }}>|</span>
            <a href="mailto:dev@rajivwallace.com">dev@rajivwallace.com</a>
          </span>
        </div>
      </div>
      <ReportModal />
    </div>
  );
}

export default App;
