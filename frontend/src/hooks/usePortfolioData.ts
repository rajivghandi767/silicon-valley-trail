import { useState, useEffect } from "react";

export interface PortfolioProject {
  title: string;
  deployed_url: string;
  description: string;
  technology: string;
  emoji?: string;
}

export interface PortfolioInfo {
  github?: string;
  github_url?: string;
  email: string;
}

function extractResults<T>(payload: unknown): T[] {
  if (Array.isArray(payload)) {
    return payload as T[];
  }
  if (
    typeof payload === "object" &&
    payload !== null &&
    "results" in payload &&
    Array.isArray(payload.results)
  ) {
    return payload.results as T[];
  }
  return [];
}

let projectsPromise: Promise<PortfolioProject[]> | null = null;
let infoPromise: Promise<PortfolioInfo | null> | null = null;

function fetchProjectsOnce(): Promise<PortfolioProject[]> {
  if (!projectsPromise) {
    projectsPromise = fetch("https://portfolio-api.rajivwallace.com/api/projects/")
      .then((res) => res.json() as Promise<unknown>)
      .then((data) => extractResults<PortfolioProject>(data))
      .catch((err: unknown) => {
        console.error(err);
        projectsPromise = null;
        return [];
      });
  }
  return projectsPromise;
}

function fetchInfoOnce(): Promise<PortfolioInfo | null> {
  if (!infoPromise) {
    infoPromise = fetch("https://portfolio-api.rajivwallace.com/api/info/")
      .then((res) => res.json() as Promise<unknown>)
      .then((data) => {
        const results = extractResults<PortfolioInfo>(data);
        return results.length > 0 ? results[0] : null;
      })
      .catch((err: unknown) => {
        console.error(err);
        infoPromise = null;
        return null;
      });
  }
  return infoPromise;
}

export function usePortfolioData(): {
  projects: PortfolioProject[];
  info: PortfolioInfo | null;
} {
  const [projects, setProjects] = useState<PortfolioProject[]>([]);
  const [info, setInfo] = useState<PortfolioInfo | null>(null);

  useEffect(() => {
    let isMounted = true;

    void fetchProjectsOnce().then((loadedProjects) => {
      if (isMounted) {
        setProjects(loadedProjects);
      }
    });

    void fetchInfoOnce().then((loadedInfo) => {
      if (isMounted && loadedInfo) {
        setInfo(loadedInfo);
      }
    });

    return () => {
      isMounted = false;
    };
  }, []);

  return { projects, info };
}
