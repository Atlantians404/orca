import api from "../../../services/api";

// Get all sessions
export const getAllSessions = async () => {
  const response = await api.get("/sessions");
  return response.data;
};

// Get one session
export const getSession = async (sessionId) => {
  const response = await api.get(`/sessions/${sessionId}`);
  return response.data;
};

// Create session
export const createSession = async (data = {}) => {
  const response = await api.post("/sessions", data);
  return response.data;
};

// Rename / update session
export const updateSession = async (sessionId, data) => {
  const response = await api.patch(`/sessions/${sessionId}`, data);
  return response.data;
};

// Delete session
export const deleteSession = async (sessionId) => {
  const response = await api.delete(`/sessions/${sessionId}`);
  return response.data;
};


// =====================================================
// PIN / UNPIN
// =====================================================

// Get pinned sessions
export const getPinnedSessions = async (page = 1, limit = 100) => {
  const response = await api.get("/sessions/pinned", {
    params: {
      page,
      limit,
    },
  });

  return response.data;
};

// Pin session
export const pinSession = async (sessionId) => {
  const response = await api.post(`/sessions/${sessionId}/pin`);
  return response.data;
};

// Unpin session
export const unpinSession = async (sessionId) => {
  const response = await api.delete(`/sessions/${sessionId}/pin`);
  return response.data;
};


// =====================================================
// ARCHIVE / UNARCHIVE
// =====================================================

// Get archived sessions
export const getArchivedSessions = async (page = 1, limit = 100) => {
  const response = await api.get("/sessions/archived", {
    params: {
      page,
      limit,
    },
  });

  return response.data;
};

// Archive session
export const archiveSession = async (sessionId) => {
  const response = await api.post(`/sessions/${sessionId}/archive`);
  return response.data;
};

// Unarchive session
export const unarchiveSession = async (sessionId) => {
  const response = await api.delete(`/sessions/${sessionId}/archive`);
  return response.data;
};