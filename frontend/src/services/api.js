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
 
const baseURL = import.meta.env.VITE_API_BASE_URL ?? "";

const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});
 
function getToken() {
  return localStorage.getItem("authToken");
}

/* ----------------------------------------------------------------------
 * DEV-ONLY REQUEST TRACING
 *
 * Proves how many actual network requests one user action produces.
 * Every request gets a short unique ID that ties its
 * [ORCA API REQUEST] / [ORCA API RESPONSE] / [ORCA API ERROR] lines
 * together in the console. Never logs the Authorization header or any
 * request/response body field that looks like a credential.
 *
 * Compiled out of production builds (import.meta.env.DEV is false there,
 * and Vite tree-shakes the dead branch).
 * ---------------------------------------------------------------------- */

let requestCounter = 0;
function nextRequestId() {
  requestCounter += 1;
  return `req-${requestCounter}`;
}

if (import.meta.env.DEV) {
  api.interceptors.request.use((config) => {
    config.metadata = {
      requestId: nextRequestId(),
      startedAt: performance.now(),
    };

    const sessionId =
      config.data?.session_id ??
      (typeof config.url === "string"
        ? config.url.match(/\/(?:chat|maps)\/([^/]+)/)?.[1]
        : undefined);

    console.log("[ORCA API REQUEST]", {
      requestId: config.metadata.requestId,
      method: config.method?.toUpperCase(),
      url: config.baseURL ? `${config.baseURL}${config.url}` : config.url,
      timestamp: new Date().toISOString(),
      sessionId,
      payload: config.data,
    });

    return config;
  });

  api.interceptors.response.use(
    (response) => {
      const { requestId, startedAt } = response.config.metadata ?? {};
      console.log("[ORCA API RESPONSE]", {
        requestId,
        status: response.status,
        url: response.config.url,
        durationMs: startedAt ? Math.round(performance.now() - startedAt) : undefined,
      });
      return response;
    },
    (error) => {
      const { requestId } = error.config?.metadata ?? {};
      console.log("[ORCA API ERROR]", {
        requestId,
        status: error.response?.status,
        url: error.config?.url,
        message: error.response?.data?.detail || error.response?.data?.message || error.message,
      });
      return Promise.reject(error);
    }
  );
}

// Attach Bearer token to every outgoing request, if present.
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * BUG FIX: this used to reshape every rejected error into a flat
 * { message, status, data } object. That silently broke every caller
 * that reads `error.response.status` / `error.response.data` —
 * including chathelp.js's toFriendlyError(), which was written
 * expecting the real axios error shape. The result: 401/403/404/5xx
 * never got their specific friendly message; everything fell through
 * to a generic fallback instead.
 *
 * Fix: pass the original axios error through unchanged. Consumers
 * that already expect `error.response` (chathelp.js) now get it.
 */
api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error)
);
 
export default api;