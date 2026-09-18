import api from "../../../services/api";

// =====================================================
// SESSION APIs
// =====================================================
// These are already used by RecentSessions / session layer.
// DO NOT REMOVE THEM.
// =====================================================

export const getAllSessions = async () => {
  const response = await api.get("/sessions");
  return response.data;
};

export const getSession = async (sessionId) => {
  const response = await api.get(`/sessions/${sessionId}`);
  return response.data;
};

export const createSession = async (data = {}) => {
  const response = await api.post("/sessions", data);
  return response.data;
};

export const updateSession = async (sessionId, data) => {
  const response = await api.patch(`/sessions/${sessionId}`, data);
  return response.data;
};

export const deleteSession = async (sessionId) => {
  const response = await api.delete(`/sessions/${sessionId}`);
  return response.data;
};

// =====================================================
// PIN / UNPIN
// =====================================================

export const getPinnedSessions = async (page = 1, limit = 100) => {
  const response = await api.get("/sessions/pinned", {
    params: {
      page,
      limit,
    },
  });

  return response.data;
};

export const pinSession = async (sessionId) => {
  const response = await api.post(`/sessions/${sessionId}/pin`);
  return response.data;
};

export const unpinSession = async (sessionId) => {
  const response = await api.delete(`/sessions/${sessionId}/pin`);
  return response.data;
};

// =====================================================
// ARCHIVE / UNARCHIVE
// =====================================================

export const getArchivedSessions = async (page = 1, limit = 100) => {
  const response = await api.get("/sessions/archived", {
    params: {
      page,
      limit,
    },
  });

  return response.data;
};

export const archiveSession = async (sessionId) => {
  const response = await api.post(`/sessions/${sessionId}/archive`);
  return response.data;
};

export const unarchiveSession = async (sessionId) => {
  const response = await api.delete(`/sessions/${sessionId}/archive`);
  return response.data;
};

// =====================================================
// NOTE
// =====================================================
// getChatHistory / sendChatMessage / resumeChat used to be duplicated
// here as well as in chathelp.js. Grepping every import in the
// codebase confirmed nothing used this file's copies — ChatWindow.jsx
// only ever imports from "../services/chathelp". Removed to avoid two
// implementations of the same three endpoints silently drifting apart.
// If you need chat operations from this file in the future, import
// them from chathelp.js instead of re-adding them here.