const API_BASE_URL = import.meta.env.VITE_API_URL || "";

/**
 * Utility to extract a cookie value by name.
 * Used primarily for retrieving the Django 'csrftoken'.
 */
function getCookie(name: string): string {
  let cookieValue = "";
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

interface ApiOptions extends RequestInit {
  body?: any; // Allows passing standard objects which are stringified automatically
}

/**
 * A generic wrapper around the native fetch API.
 * * @template T - The expected shape of the JSON response.
 * @param endpoint - The API path (e.g., '/api/state/').
 * @param options - Standard fetch options plus an optional object body.
 * @returns A promise resolving to the typed data.
 */
export async function apiFetch<T>(
  endpoint: string,
  options: ApiOptions = {},
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers = new Headers(options.headers || {});

  // Automatically handle JSON stringification and set Content-Type header
  if (options.body && typeof options.body === "object") {
    options.body = JSON.stringify(options.body);
    headers.set("Content-Type", "application/json");
  }

  // Automatically attach CSRF token for state-changing HTTP methods
  const method = (options.method || "GET").toUpperCase();
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const csrfToken = getCookie("csrftoken");
    if (csrfToken) {
      headers.set("X-CSRFToken", csrfToken);
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: "include", // Required for session and CSRF cookies to be sent
  });

  // Handle cases where the response might not be JSON (e.g., 204 No Content)
  const isJson = response.headers.get("content-type")?.includes("application/json");
  const data = isJson ? ((await response.json()) as T) : ({} as T);

  if (!response.ok) {
    // Attempt to extract error message from backend response
    const errorMsg = (data as any)?.error || `HTTP error! status: ${response.status}`;
    throw new Error(errorMsg);
  }

  return data;
}