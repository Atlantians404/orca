import api from "./api";

/**
 * Thin wrapper around the existing auth endpoints. Does not invent any
 * new backend contracts — GET /auth/me and POST /auth/logout are assumed
 * to already exist per the task spec. If your actual paths differ,
 * update SESSIONS_URL-style constants below, nothing else needs to change.
 */

const ME_URL = "/auth/me";
const LOGOUT_URL = "/auth/logout";

/** Get the currently authenticated user. Shape is whatever the backend returns. */
export async function getCurrentUser() {
  const res = await api.get(ME_URL);
  return res.data;
}

/** Log the current user out. */
export async function logout() {
  await api.post(LOGOUT_URL);
}