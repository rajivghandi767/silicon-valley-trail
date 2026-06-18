import { useState, useEffect } from "react";

export interface PortfolioProject {
  title: string;
  deployed_url: string;
  description: string;
  technology: string;
  emoji?: string;
}

export interface PortfolioInfo {
  github_url: string;
  email: string;
}

export function usePortfolioData() {
  const [projects, setProjects] = useState<PortfolioProject[]>([]);
  const [info, setInfo] = useState<PortfolioInfo | null>(null);

  useEffect(() => {
    let isMounted = true;
    fetch("https://portfolio-api.rajivwallace.com/api/projects/")
      .then(res => res.json())
      .then(data => {
        if (!isMounted) return;
        const results = data.results || data;
        setProjects(Array.isArray(results) ? results : []);
      })
      .catch(console.error);
      
    fetch("https://portfolio-api.rajivwallace.com/api/info/")
      .then(res => res.json())
      .then(data => {
        if (!isMounted) return;
        const results = data.results || data;
        if (Array.isArray(results) && results.length > 0) {
          setInfo(results[0]);
        }
      })
      .catch(console.error);
      
    return () => { isMounted = false; };
  }, []);

  return { projects, info };
}
