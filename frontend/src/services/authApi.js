import api from "./api";

/**
 * Auth API service for user login, registration, fetching profile, and logout.
 */

const LOGIN_URL = "/auth/login";
const REGISTER_URL = "/auth/register";
const ME_URL = "/auth/me";
const LOGOUT_URL = "/auth/logout";

/** Log in user with credentials { email, password } and store access_token in localStorage */
export async function loginUser(credentials) {
  const res = await api.post(LOGIN_URL, credentials);
  const token = res.data?.access_token || res.data?.token;
  if (token) {
    localStorage.setItem("authToken", token);
  }
  return res.data;
}

/** Register user with payload { username, email, password, ... } */
export async function registerUser(payload) {
  const res = await api.post(REGISTER_URL, payload);
  return res.data;
}

/** Get the currently authenticated user. Shape is whatever the backend returns. */
export async function getCurrentUser() {
  const res = await api.get(ME_URL);
  return res.data;
}

/** Log the current user out and clear token from localStorage. */
export async function logout() {
  try {
    await api.post(LOGOUT_URL);
  } catch (err) {
    console.warn("Backend logout request failed:", err);
  } finally {
    localStorage.removeItem("authToken");
  }
}