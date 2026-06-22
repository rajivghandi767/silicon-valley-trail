import { useState, useRef, useEffect } from "react";
import { usePortfolioData } from "../hooks/usePortfolioData";

export function ProjectSwitcher() {
  const { projects } = usePortfolioData();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div
      className="project-switcher"
      ref={dropdownRef}
      style={{ display: "flex", alignItems: "center", position: "relative" }}
    >
      <button
        className="switcher-btn"
        onClick={() => setIsOpen(!isOpen)}
        title="More Projects"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect x="3" y="3" width="7" height="7"></rect>
          <rect x="14" y="3" width="7" height="7"></rect>
          <rect x="14" y="14" width="7" height="7"></rect>
          <rect x="3" y="14" width="7" height="7"></rect>
        </svg>
      </button>

      {isOpen && (
        <div className="switcher-dropdown">
          <div
            style={{
              padding: "0.75rem",
              borderBottom: "1px solid var(--border-color)",
              fontSize: "0.75rem",
              opacity: 0.7,
            }}
          >
            // MORE BY RAJIV
          </div>
          {projects.map((p) => (
            <a
              key={p.title}
              href={p.deployed_url}
              target="_blank"
              rel="noreferrer"
              className="switcher-item"
            >
              <div
                style={{
                  width: "2rem",
                  flexShrink: 0,
                  display: "flex",
                  alignItems: "flex-start",
                  justifyContent: "flex-start",
                  fontSize: "1.25rem",
                  paddingTop: "0.125rem",
                  color: "var(--text-main)",
                }}
              >
                {p.emoji || (p.technology ? p.technology.substring(0, 2).toUpperCase() : "✨")}
              </div>
              <div>
                <div className="switcher-title">{p.title}</div>
                <div className="switcher-desc">{p.description}</div>
              </div>
            </a>
          ))}
          <div
            style={{
              padding: "0.5rem",
              borderTop: "1px solid var(--border-color)",
              backgroundColor: "var(--sidebar-bg)",
              textAlign: "center",
            }}
          >
            <a
              href="https://github.com/rajivghandi767"
              target="_blank"
              rel="noreferrer"
              style={{
                fontSize: "0.75rem",
                fontWeight: 500,
                color: "var(--accent-blue)",
                textDecoration: "none",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.textDecoration = "underline")}
              onMouseLeave={(e) => (e.currentTarget.style.textDecoration = "none")}
            >
              View GitHub Repo →
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
