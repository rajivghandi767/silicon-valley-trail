const API_BASE_URL = import.meta.env.VITE_API_URL || "";

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

interface ApiOptions extends Omit<RequestInit, 'body'> {
  body?: Record<string, unknown>; 
}

export async function apiFetch<T>(
  endpoint: string,
  options: ApiOptions = {},
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = new Headers(options.headers || {});

  // Automatically set headers if a JSON body is present
  if (options.body) {
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

  // Re-map the body back to a string for the native fetch API
  const fetchOptions: RequestInit = {
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined,
    headers,
    credentials: "include", 
  };

  const response = await fetch(url, fetchOptions);

  const isJson = response.headers.get("content-type")?.includes("application/json");
  
  // REFACTOR: Removed loose 'any' casting
  const data = isJson ? ((await response.json()) as Record<string, unknown>) : {};

  if (!response.ok) {
    const errorMsg = (data as { error?: string }).error || `HTTP error! status: ${response.status}`;
    throw new Error(errorMsg);
  }

  return data as T;
}