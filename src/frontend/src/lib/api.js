const datasetBaseUrl = (import.meta.env.VITE_DATASET_BASE_URL || '').replace(/\/$/, '');

export function assetUrl(path) {
  return `${datasetBaseUrl}${path}`;
}
