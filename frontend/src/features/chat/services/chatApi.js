import api from "../../../services/api";

/**
 * Session model (JSDoc, since this is a JS project — not TS).
 * Matches the real /sessions API contract:
 *
 * @typedef {Object} Session
 * @property {number} id - integer, not a UUID
 * @property {string} title
 * @property {string} [summary] - present on Create/GetOne/GetAll/Update responses
 * @property {...*} [rest] - any extra fields the backend adds are preserved
 */

const SESSIONS_URL = "/sessions";

/**
 * Passes through whatever the backend sends so we never silently drop
 * fields it adds later. Only guarantees id/title exist.
 *
 * NOTE: the real API has no createdAt/updatedAt — don't rely on those.
 */
function normalizeSession(raw) {
  if (!raw) return raw;
  return {
    id: raw.id,
    title: raw.title ?? "New Conversation",
    summary: raw.summary ?? "",
    ...raw, // keep any additional backend fields
  };
}

/** Create a new chat session. Body: { title }. Returns 201 + session. */
export async function createSession(data) {
  const res = await api.post(SESSIONS_URL, data);
  return normalizeSession(res.data);
}

/**
 * Get all chat sessions (paginated).
 * GET /sessions?page=&limit= -> { items, page, limit, total }
 *
 * @param {{page?: number, limit?: number}} [params]
 * @returns {Promise<{items: Session[], page: number, limit: number, total: number}>}
 */
export async function getAllSessions(params = {}) {
  const res = await api.get(SESSIONS_URL, { params });
  const { items = [], page, limit, total } = res.data ?? {};
  return { items: items.map(normalizeSession), page, limit, total };
}

/** Get a single chat session by id. */
export async function getSession(id) {
  const res = await api.get(`${SESSIONS_URL}/${id}`);
  return normalizeSession(res.data);
}

/** Update a session (e.g. rename). Body: { title }. */
export async function updateSession(id, data) {
  const res = await api.patch(`${SESSIONS_URL}/${id}`, data);
  return normalizeSession(res.data);
}

/** Delete a session. Responds 204 with no body — just confirm success. */
export async function deleteSession(id) {
  await api.delete(`${SESSIONS_URL}/${id}`);
  return id;
}
