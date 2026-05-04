import { useState, useEffect } from "react";
import { apiFetch } from "./utils/api";
import type { GameState } from "./types";
import { ProjectSwitcher } from "./components/ProjectSwitcher";
import { ReportModal } from "./components/ReportModal";
import "./index.css";

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [narrative, setNarrative] = useState<string>(
    "// Establishing secure connection...",
  );

  useEffect(() => {
    apiFetch("/api/state/")
      .then((data) => {
        setGameState(data);
        if (data.message) setNarrative(data.message);
      })
      .catch((err) => {
        if (err.message.includes("No active game found")) {
          handleRestart(true); // Auto-start the game silently!
        } else {
          setError(err.message);
        }
      });
  }, []);

  const handleAction = async (actionType: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await apiFetch("/api/action/", {
        method: "POST",
        body: { action: actionType },
      });

      setGameState(data);
      if (data.message) setNarrative(data.message);
    } catch (err: any) {
      setError(err.message);
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
      const data = await apiFetch("/api/restart/", { method: "POST" });

      setGameState(data);
      if (data.message) setNarrative(data.message);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (error && !gameState)
    return <div style={{ color: "red", padding: "2rem" }}>Error: {error}</div>;
  if (!gameState) return <div style={{ padding: "2rem" }}>Loading IDE...</div>;

  const isGameOver = gameState.is_won || gameState.is_lost;

  return (
    <div className="app-container">
      {/* LEFT SIDEBAR: Player Stats */}
      <div className="sidebar">
        {/* LOCATION BLOCK: Stacked Vertically */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.75rem",
            paddingBottom: "1.5rem",
            borderBottom: "1px dashed var(--border-color)",
          }}
        >
          {/* Split Location and Stop into two distinct lines */}
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

        {/* RESOURCE BLOCKS */}
        <div className="stat-block">
          <span className="stat-label">Days Remaining</span>
          <span
            className="stat-value"
            style={{
              color:
                gameState.days_remaining <= 3
                  ? "var(--accent-red)"
                  : "var(--accent-green)",
            }}
          >
            {gameState.days_remaining}
          </span>
        </div>

        <div className="stat-block">
          <span className="stat-label">Cash</span>
          <span
            className="stat-value"
            style={{
              color:
                gameState.cash <= 300
                  ? "var(--accent-red)"
                  : "var(--accent-green)",
            }}
          >
            ${gameState.cash.toLocaleString()}
          </span>
        </div>

        <div className="stat-block">
          <span className="stat-label">Award Miles</span>
          <span
            className="stat-value"
            style={{
              color:
                gameState.award_miles < 2000
                  ? "var(--text-main)"
                  : "var(--accent-blue)",
            }}
          >
            {gameState.award_miles.toLocaleString()}
          </span>
        </div>

        <div className="stat-block">
          <span className="stat-label">Morale</span>
          <span
            className="stat-value"
            style={{
              color:
                gameState.morale <= 30
                  ? "var(--accent-red)"
                  : "var(--accent-green)",
            }}
          >
            {gameState.morale}%
          </span>
        </div>

        <div className="stat-block">
          <span className="stat-label">Bugs</span>
          <span
            className="stat-value"
            /* Warning orange at 30, Critical red at 40, Max 50 */
            style={{
              color:
                gameState.bugs >= 40
                  ? "var(--accent-red)"
                  : gameState.bugs >= 30
                    ? "var(--accent-orange)"
                    : "var(--accent-green)",
            }}
          >
            {gameState.bugs} / 50
          </span>
        </div>
        <div
          style={{
            marginTop:
              "auto" /* Pushes this block to the absolute bottom of the sidebar */,
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
            &lt; Silicon Valley Trail: Caribbean Edition /&gt;
          </h1>
          <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
            <button onClick={() => handleRestart()} className="restart-btn">
              [ Restart Game ]
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
              [ Write Code ]
            </button>
            <button
              className="action-btn"
              onClick={() => handleAction("mentor")}
              disabled={isLoading || isGameOver}
            >
              [ Mentor ]
            </button>
            <button
              className="action-btn"
              onClick={() => handleAction("rest")}
              disabled={isLoading || isGameOver}
            >
              [ Rest ]
            </button>
            <button
              className="action-btn fly"
              onClick={() => handleAction("travel_ferry")}
              disabled={isLoading || isGameOver}
            >
              [ Ferry ]
            </button>
            <button
              className="action-btn fly"
              onClick={() => handleAction("travel_flight")}
              disabled={isLoading || isGameOver}
            >
              [ Fly ]
            </button>
          </div>
        </div>

        <div className="footer">
          <span>Built for the LinkedIn REACH Apprenticeship</span>
          <span>
            Developed by{" "}
            <a href="https://rajivwallace.com" target="_blank" rel="noreferrer">
              Rajiv Wallace 🇩🇲
            </a>{" "}
            |
            <a
              href="https://github.com/rajivghandi767"
              target="_blank"
              rel="noreferrer"
              style={{ marginLeft: "8px" }}
            >
              GitHub
            </a>
          </span>
        </div>
      </div>
      <ReportModal />
    </div>
  );
}

export default App;
