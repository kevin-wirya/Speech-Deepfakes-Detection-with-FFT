const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export const isProductionApiMissing = import.meta.env.PROD && !apiBaseUrl;

export function apiUrl(path) {
  return `${apiBaseUrl}${path}`;
}
