import api from "../../../services/api";

// Get all sessions
export const getAllSessions = async () => {
  if (!localStorage.getItem("authToken")) return [];
  const response = await api.get("/sessions");
  return response.data;
};

// Get one session
export const getSession = async (sessionId) => {
  if (!localStorage.getItem("authToken")) return null;
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
  if (!localStorage.getItem("authToken")) return [];
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
  if (!localStorage.getItem("authToken")) return [];
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
// =====================================================
// CHAT
// =====================================================

// Get chat history for a session
export const getChatHistory = async (sessionId) => {
  const response = await api.get(
    `/chat/${sessionId}/history`
  );

  return response.data;
};

// Send message
export const sendChatMessage = async (
  sessionId,
  message
) => {
  const response = await api.post(
    "/chat",
    {
      session_id: sessionId,
      message,
    }
  );

  return response.data;
};

// Resume pending chat workflow
export const resumeChat = async (
  sessionId,
  value
) => {
  const response = await api.post(
    `/chat/${sessionId}/resume`,
    {
      value,
    }
  );

  return response.data;
};