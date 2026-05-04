const API_BASE_URL = import.meta.env.VITE_API_URL;

function getCookie(name: string): string {
  let cookieValue = "";
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

interface ApiOptions extends RequestInit {
  body?: any; // Allow passing standard JS objects as body
}

export async function apiFetch(endpoint: string, options: ApiOptions = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Setup default headers
  const headers = new Headers(options.headers || {});
  
  // Automatically handle JSON stringification and Content-Type
  if (options.body && typeof options.body === 'object') {
    options.body = JSON.stringify(options.body);
    headers.set('Content-Type', 'application/json');
  }

  // Automatically attach CSRF token for state-changing methods
  const method = (options.method || 'GET').toUpperCase();
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      headers.set('X-CSRFToken', csrfToken);
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: "include", // Always include cookies for session auth
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || `HTTP error! status: ${response.status}`);
  }

  return data;
}