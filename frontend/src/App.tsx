import { useState, useEffect } from "react";
import { apiFetch } from "./utils/api";
import { GameState, GameAction } from "./types";
import { ProjectSwitcher } from "./components/ProjectSwitcher";
import { ReportModal } from "./components/ReportModal";
import { LazySection } from "./components/LazySection";
import { usePortfolioData } from "./hooks/usePortfolioData";
import "./index.css";

const getStatusColor = (status: string) => {
    switch (status) {
        case "critical": return "var(--accent-red)";
        case "warning": return "var(--accent-orange)";
        case "good": return "var(--accent-green)";
        case "default": return "var(--text-main)";
        case "blue": return "var(--accent-blue)";
        default: return "inherit";
    }
};

function App() {
  const { info } = usePortfolioData();
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [narrative, setNarrative] = useState<string>(
    "// Establishing secure connection...",
  );

  // We use useEffect to fetch the initial game state when the component mounts.
  // The 'isMounted' flag is a common React pattern used to prevent state updates
  // on unmounted components, which can happen if the user navigates away before the API responds.
  useEffect(() => {
    let isMounted = true;
    apiFetch<GameState>("/api/state/")
      .then((data) => {
        if (!isMounted) return;
        setGameState(data);
        if (data.message) setNarrative(data.message);
      })
      .catch((err: Error) => {
        if (!isMounted) return;
        setError(err.message);
      });
    return () => { isMounted = false; };
  }, []);

  /**
   * Handles user actions (e.g., 'code', 'mentor', 'rest') by sending a POST request to the API.
   * Uses async/await syntax for cleaner asynchronous code flow compared to Promise chaining.
   * The 'finally' block ensures the loading state is reset regardless of whether the request succeeds or fails.
   */
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
              style={{ opacity: 0.8, fontSize: "0.75rem" }}
            >
              STOP {gameState.sequence_in_journey} OF {gameState.total_stops}
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
            <span className="stat-emoji">📅</span>
            <span className="stat-text">Days</span>
          </span>
          <span
            className="stat-value"
            style={{ color: getStatusColor(gameState.stat_statuses.days) }}
          >
            {gameState.days_remaining}
          </span>
        </div>

        <div className="stat-block">
          <span className="stat-label">
            <span className="stat-emoji">💰</span>
            <span className="stat-text">Cash</span>
          </span>
          <span
            className="stat-value"
            style={{ color: getStatusColor(gameState.stat_statuses.cash) }}
          >
            ${gameState.cash.toLocaleString()}
          </span>
        </div>

        <div className="stat-block">
          <span className="stat-label">
            <span className="stat-emoji">✈️</span>
            <span className="stat-text">Miles</span>
          </span>
          <span
            className="stat-value"
            style={{ color: getStatusColor(gameState.stat_statuses.miles) }}
          >
            {gameState.award_miles.toLocaleString()}
          </span>
        </div>

        <div className="stat-block">
          <span className="stat-label">
            <span className="stat-emoji">🎭</span>
            <span className="stat-text">Morale</span>
          </span>
          <span
            className="stat-value"
            style={{ color: getStatusColor(gameState.stat_statuses.morale) }}
          >
            {gameState.morale}%
          </span>
        </div>

        <div className="stat-block">
          <span className="stat-label">
            <span className="stat-emoji">🐛</span>
            <span className="stat-text">Bugs</span>
          </span>
          <span
            className="stat-value"
            style={{ color: getStatusColor(gameState.stat_statuses.bugs) }}
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

      <main className="main-window">
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
              <span className="show-on-mobile">Restart</span>
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
              <span className="btn-emoji">💻</span>
              <span className="btn-text">Code</span>
            </button>
            <button
              className="action-btn"
              onClick={() => handleAction("mentor")}
              disabled={isLoading || isGameOver}
            >
              <span className="btn-emoji">🤝🏽</span>
              <span className="btn-text">Mentor</span>
            </button>
            <button
              className="action-btn"
              onClick={() => handleAction("rest")}
              disabled={isLoading || isGameOver}
            >
              <span className="btn-emoji">🛌</span>
              <span className="btn-text">Rest</span>
            </button>

            <div className="action-separator"></div>

            <button
              className="action-btn fly"
              onClick={() => handleAction("travel_ferry")}
              disabled={isLoading || isGameOver}
            >
              <span className="btn-emoji">⛴️</span>
              <span className="btn-text">Take Ferry</span>
            </button>
            <button
              className="action-btn fly"
              onClick={() => handleAction("travel_flight")}
              disabled={isLoading || isGameOver}
            >
              <span className="btn-emoji">✈️</span>
              <span className="btn-text">Fly</span>
            </button>
          </div>
        </div>

        <LazySection className="footer">
          <span>Built for the LinkedIn REACH Apprenticeship</span>
          <span>
            Developed by{" "}
            <a href="https://rajivwallace.com" target="_blank" rel="noreferrer">
              Rajiv Wallace 🇩🇲
            </a>
          </span>
          <span className="footer-links">
            <a
              href={info?.github_url || "https://github.com/rajivghandi767"}
              target="_blank"
              rel="noreferrer"
            >
              GitHub
            </a>
            <span style={{ margin: "0 0.5rem" }}>|</span>
            <a href={`mailto:${info?.email || "dev@rajivwallace.com"}`}>{info?.email || "dev@rajivwallace.com"}</a>
          </span>

          <ReportModal />
        </LazySection>
      </main>
    </div>
  );
}

export default App;
