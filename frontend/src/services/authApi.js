import api from "./api";

/**
 * Auth API service for user login, registration, fetching profile, and logout.
 * Base URL: https://orca-qlqz.onrender.com
 */

const LOGIN_URL = "/auth/login";
const REGISTER_URL = "/auth/register";
const ME_URL = "/auth/me";
const LOGOUT_URL = "/auth/logout";

/**
 * Log in user with credentials { email, password }
 * POST /auth/login -> Returns { access_token, token_type: "bearer" }
 */
export async function loginUser({ email, password }) {
  const res = await api.post(LOGIN_URL, { email, password });
  const token = res.data?.access_token || res.data?.token;
  if (token) {
    localStorage.setItem("authToken", token);
  }
  return res.data;
}

/**
 * Register user with payload { username, email, password }
 * POST /auth/register -> Returns { message: string }
 */
export async function registerUser({ username, email, password }) {
  const res = await api.post(REGISTER_URL, { username, email, password });
  return res.data;
}

/**
 * Get current user profile
 * GET /auth/me -> Returns { id, username, email, role }
 */
export async function getCurrentUser() {
  const res = await api.get(ME_URL);
  return res.data;
}

/**
 * Log out current user
 * POST /auth/logout -> Returns { message: string }
 */
export async function logout() {
  try {
    await api.post(LOGOUT_URL);
  } catch (err) {
    console.warn("Backend logout request failed:", err);
  } finally {
    localStorage.removeItem("authToken");
  }
}
