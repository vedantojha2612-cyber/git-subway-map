/**
 * Subway Map API Service.
 * Connects to the FastAPI backend serving the Git DAG transit graph.
 */

// Try relative path first (Vite proxy), fallback to direct local addresses
const API_CANDIDATES = [
  '',
  'http://localhost:8001',
  'http://127.0.0.1:8001',
  'http://localhost:8000',
  'http://127.0.0.1:8000'
];

let workingBaseUrl = null;

async function requestWithFallback(endpoint, options = {}) {
  // If we already know the working base URL, try it first
  const basesToTry = workingBaseUrl !== null 
    ? [workingBaseUrl, ...API_CANDIDATES.filter(b => b !== workingBaseUrl)]
    : API_CANDIDATES;

  let lastError = null;

  for (const base of basesToTry) {
    const url = `${base}${endpoint}`;
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers || {})
        }
      });

      if (response.ok) {
        workingBaseUrl = base;
        return await response.json();
      } else {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }
    } catch (err) {
      lastError = err;
      // Continue to next candidate if network failed
    }
  }

  throw lastError || new Error(`Failed to connect to API on ${endpoint}`);
}

export async function fetchHealth() {
  return requestWithFallback('/api/health');
}

export async function fetchSubwayGraph(repoPath = null, stepX = 140, stepY = 90) {
  const params = new URLSearchParams();
  if (repoPath && repoPath.trim()) {
    params.set('repo_path', repoPath.trim());
  }
  if (stepX) params.set('step_x', stepX);
  if (stepY) params.set('step_y', stepY);

  const queryString = params.toString() ? `?${params.toString()}` : '';
  return requestWithFallback(`/api/subway-graph${queryString}`);
}

export async function fetchLines(repoPath = null) {
  const params = repoPath ? `?repo_path=${encodeURIComponent(repoPath)}` : '';
  return requestWithFallback(`/api/lines${params}`);
}

export async function fetchStations(repoPath = null) {
  const params = repoPath ? `?repo_path=${encodeURIComponent(repoPath)}` : '';
  return requestWithFallback(`/api/stations${params}`);
}

export async function resetDemoRepo() {
  return requestWithFallback('/api/demo/reset', {
    method: 'POST'
  });
}
