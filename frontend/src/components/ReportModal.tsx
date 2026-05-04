import { useState } from "react";
import { apiFetch } from "../utils/api";

export function ReportModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [issueType, setIssueType] = useState("game_logic");
  const [userNote, setUserNote] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await apiFetch("/api/reports/", {
        method: "POST",
        body: { issue_type: issueType, user_note: userNote },
      });

      setSuccess(true);
      setTimeout(() => {
        setIsOpen(false);
        setSuccess(false);
        setUserNote("");
      }, 2000);
    } catch (error) {
      console.error(error);
      alert("Failed to send report. Network or server error.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="floating-report-btn"
        title="Report Issue"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      </button>

      {isOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button onClick={() => setIsOpen(false)} className="modal-close">
              ✕
            </button>
            <h2
              className="title"
              style={{ fontSize: "1.25rem", marginBottom: "1rem" }}
            >
              &gt; Report an Issue_
            </h2>

            {success ? (
              <div
                style={{
                  color: "var(--accent-green)",
                  padding: "2rem 0",
                  textAlign: "center",
                }}
              >
                // Transmission successful. Thank you.
              </div>
            ) : (
              <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: "1rem" }}>
                  <label
                    style={{ fontSize: "0.85rem", color: "var(--accent-blue)" }}
                  >
                    const issueType =
                  </label>
                  <select
                    value={issueType}
                    onChange={(e) => setIssueType(e.target.value)}
                    className="modal-select"
                  >
                    <option value="game_logic">Game Logic / Math Error</option>
                    <option value="ui_bug">UI / Display Glitch</option>
                    <option value="typo">Typo / Spelling Error</option>
                    <option value="other">Other Exception</option>
                  </select>
                </div>

                <div style={{ marginBottom: "1.5rem" }}>
                  <label
                    style={{ fontSize: "0.85rem", color: "var(--accent-blue)" }}
                  >
                    const details =
                  </label>
                  <textarea
                    required
                    rows={4}
                    value={userNote}
                    onChange={(e) => setUserNote(e.target.value)}
                    className="modal-textarea"
                    placeholder="Describe the exception..."
                  />
                </div>

                <div
                  style={{
                    display: "flex",
                    gap: "1rem",
                    justifyContent: "flex-end",
                  }}
                >
                  <button
                    type="button"
                    onClick={() => setIsOpen(false)}
                    className="restart-btn"
                    style={{
                      borderColor: "var(--text-main)",
                      color: "var(--text-main)",
                    }}
                  >
                    [ Cancel ]
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="action-btn"
                  >
                    {isSubmitting ? "[ Sending... ]" : "[ Submit ]"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
}
