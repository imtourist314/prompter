const DEFAULT_DIRECT_BASE_URL = 'http://localhost:5333';
const DEFAULT_PROXY_PATH = '/agent-api';

const normalizeBase = (value) => value?.replace(/\/$/, '');

const isAbsoluteUrl = (value) => /^https?:\/\//i.test(value);

const getClientOrigin = () => {
  if (typeof window !== 'undefined' && window.location) {
    return window.location.origin;
  }
  if (typeof globalThis !== 'undefined' && globalThis.location?.origin) {
    return globalThis.location.origin;
  }
  return 'http://localhost';
};

const getBaseUrl = () => {
  const configuredBase = normalizeBase(import.meta.env.VITE_AGENT_API_BASE);
  if (configuredBase) return configuredBase;

  if (import.meta.env.DEV) {
    return normalizeBase(DEFAULT_PROXY_PATH);
  }

  return normalizeBase(DEFAULT_DIRECT_BASE_URL);
};

const buildUrl = (path, query) => {
  const base = getBaseUrl();
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const absoluteBase = isAbsoluteUrl(base) ? base : `${getClientOrigin()}${base}`;
  const url = new URL(`${absoluteBase}${normalizedPath}`);

  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value === undefined || value === null || value === '') return;
      if (Array.isArray(value)) {
        value.forEach((item) => {
          if (item !== undefined && item !== null && item !== '') {
            url.searchParams.append(key, item);
          }
        });
      } else {
        url.searchParams.set(key, value);
      }
    });
  }

  return url;
};

async function request(path, { method = 'GET', body, query } = {}) {
  const url = buildUrl(path, query);

  const response = await fetch(url.toString(), {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const message = await safeParseError(response);
    throw new Error(message || `Request failed with ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

async function safeParseError(response) {
  try {
    const data = await response.json();
    if (typeof data === 'string') return data;
    if (data?.detail) return Array.isArray(data.detail) ? data.detail.join(', ') : data.detail;
    return null;
  } catch (err) {
    return null;
  }
}

export const AgentApi = {
  getProjects() {
    return request('/projects');
  },
  getAreas(project) {
    return request('/areas', { query: { project } });
  },
  getComponents(project, area) {
    return request('/components', { query: { project, area } });
  },
  listFiles({ project, area, component, limit = 100, statuses }) {
    return request('/files', { query: { project, area, component, limit, status: statuses } });
  },
  publishFile(payload) {
    return request('/files', { method: 'POST', body: payload });
  },
};
