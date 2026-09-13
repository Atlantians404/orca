import axios from "axios";
 
/**
 * Shared Axios instance for the whole app.
 *
 * ASSUMPTION: no src/services/api.js existed yet (file was empty), so this
 * creates a minimal, reusable client. If your project already has a
 * differently-configured instance elsewhere, delete this file and point
 * chatApi.js at that one instead — do not run two API clients side by side.
 *
 * ASSUMPTION: the auth token is stored in localStorage under "authToken".
 * If you're using an AuthContext / different storage, swap out the
 * getToken() implementation below — nothing else needs to change.
 */
 
const baseURL = import.meta.env.VITE_API_BASE_URL || "/api";
 
const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});
 
function getToken() {
  return localStorage.getItem("authToken");
}
 
// Attach Bearer token to every outgoing request, if present.
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
 
// Normalize errors so callers get a consistent shape:
// { message, status, data }
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const data = error.response?.data;
    const message =
      data?.message ||
      error.message ||
      "Something went wrong talking to the server.";
    return Promise.reject({ message, status, data });
  }
);
 
export default api;
 
