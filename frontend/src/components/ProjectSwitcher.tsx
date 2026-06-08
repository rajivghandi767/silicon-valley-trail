import { useState, useRef, useEffect } from "react";
import { usePortfolioData } from "../hooks/usePortfolioData";

interface ProjectSwitcherProps {}

export function ProjectSwitcher(_props: ProjectSwitcherProps) {
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
              <span style={{ fontSize: "1.5rem" }}>{p.technology || "✨"}</span>
              <div>
                <div className="switcher-title">{p.title}</div>
                <div className="switcher-desc">{p.description}</div>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}

export default ProjectSwitcher;
