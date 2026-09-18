/**
 * ASSUMPTION (flagged per the implementation brief):
 *
 * `src/services/api.js` was not available to inspect, so this file
 * assumes it exports a pre-configured axios instance as its DEFAULT
 * export — baseURL set from `import.meta.env.VITE_API_BASE_URL`, with
 * auth token attachment already handled there (the same instance
 * authApi.js presumably builds on for getCurrentUser/logout).
 *
 * If that assumption is wrong, only the single import line below
 * needs to change — nothing else in this file, or in any component
 * that calls these functions, depends on how `api` itself is built.
 */
import api from './api';

export async function getSavedMaps() {
  const { data } = await api.get('/api/maps');
  return data;
}

export async function getMap(mapId) {
  const { data } = await api.get(`/api/maps/${mapId}`);
  return data;
}

export async function saveMap(payload) {
  const { data } = await api.post('/api/maps', payload);
  return data;
}

export async function deleteMap(mapId) {
  await api.delete(`/api/maps/${mapId}`);
}

export async function generateRoute(payload) {
  const { data } = await api.post('/api/routes/generate', payload);
  return data;
}

// Marine zones are effectively static reference data. Every
// InteractiveRouteMap instance (one per chat message with a route) and
// MapsPage previously called this independently, meaning a session with
// several route responses made the same GET repeatedly for identical
// data. Cache the in-flight/resolved promise so concurrent and
// subsequent callers share one request; call resetMarineZonesCache()
// if you ever need to force a refetch (e.g. an admin action).
let marineZonesPromise = null;

export function getMarineZones() {
  if (!marineZonesPromise) {
    marineZonesPromise = api
      .get('/api/marine-zones')
      .then(({ data }) => data)
      .catch((err) => {
        // Don't cache a failure — let the next caller retry.
        marineZonesPromise = null;
        throw err;
      });
  }
  return marineZonesPromise;
}

export function resetMarineZonesCache() {
  marineZonesPromise = null;
}
