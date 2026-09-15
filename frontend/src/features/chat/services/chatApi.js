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
// CHAT APIs — YOUR ACTUAL 3 ENDPOINTS
// =====================================================

/**
 * GET /chat/{session_id}/history
 *
 * Loads the complete conversation for a session.
 */
export const getChatHistory = async (sessionId) => {
  const response = await api.get(`/chat/${sessionId}/history`);
  return response.data;
};

/**
 * POST /chat
 *
 * Request:
 * {
 *   session_id: number,
 *   message: string
 * }
 */
export const sendChatMessage = async (sessionId, message) => {
  const response = await api.post("/chat", {
    session_id: sessionId,
    message,
  });

  return response.data;
};

/**
 * POST /chat/{session_id}/resume
 *
 * Request:
 * {
 *   value: string
 * }
 */
export const resumeChat = async (sessionId, value) => {
  const response = await api.post(`/chat/${sessionId}/resume`, {
    value,
  });

  return response.data;
};