/*
 * ============================================================================
 * chathelp.js — ORCA chat message service
 * ============================================================================
 *
 * Real backend endpoints:
 *
 *   POST /chat
 *     body: { session_id, message }
 *
 *   POST /chat/{session_id}/resume
 *     body: { value }
 *
 *   GET /chat/{session_id}/history
 *
 * Suggestions are UI-only and are handled by ChatWindow.
 *
 * Session CRUD is NOT handled here.
 * ============================================================================ */

import api from "../../../services/api";

/* --------------------------------------------------------------------------
 * Error handling
 * -------------------------------------------------------------------------- */

function toFriendlyError(error) {
  const status = error?.response?.status;
  const data = error?.response?.data;

  const backendMessage =
    typeof data === "string"
      ? data
      : data?.detail ||
        data?.message ||
        data?.error;

  if (backendMessage) {
    return new Error(backendMessage);
  }

  if (status === 401) {
    return new Error("Your session has expired. Please log in again.");
  }

  if (status === 403) {
    return new Error("You don't have permission to access this conversation.");
  }

  if (status === 404) {
    return new Error("This conversation could not be found.");
  }

  if (status >= 500) {
    return new Error("ORCA's server is temporarily unavailable.");
  }

  if (error?.message) {
    return new Error(error.message);
  }

  return new Error("ORCA couldn't complete that request.");
}

/* --------------------------------------------------------------------------
 * Local UI message helpers
 * -------------------------------------------------------------------------- */

let localIdCounter = 0;

function makeLocalId(prefix) {
  localIdCounter += 1;
  return `${prefix}-${Date.now()}-${localIdCounter}`;
}

export function makeUserMessage(content) {
  return {
    id: makeLocalId("user"),
    role: "user",
    content,
    response_data: null,
    pending_action: null,
    workflow_status: "COMPLETED",
    options: [],
    created_at: new Date().toISOString(),
  };
}

export function makePendingAssistantMessage() {
  return {
    id: makeLocalId("pending"),
    role: "assistant",
    content: "",
    response_data: null,
    pending_action: null,
    workflow_status: null,
    options: [],
    pending: true,
    created_at: new Date().toISOString(),
  };
}

/* --------------------------------------------------------------------------
 * Backend response normalization
 * -------------------------------------------------------------------------- */

function normalizeHistoryMessage(raw) {
  return {
    id: raw?.id ?? makeLocalId("history"),
    role: raw?.role ?? "assistant",
    content: raw?.content ?? "",
    response_data: raw?.response_data ?? null,

    // History response doesn't normally contain workflow information.
    pending_action: raw?.pending_action ?? null,
    workflow_status: raw?.workflow_status ?? "COMPLETED",
    options: Array.isArray(raw?.options) ? raw.options : [],

    created_at: raw?.created_at ?? null,
  };
}

function normalizeChatResponse(data) {
  return {
    id: makeLocalId("assistant"),
    role: "assistant",

    content: data?.message ?? "",

    response_data: data?.response_data ?? null,

    pending_action: data?.pending_action ?? null,

    workflow_status:
      data?.workflow_status ?? "COMPLETED",

    options:
      Array.isArray(data?.options)
        ? data.options
        : [],

    created_at: new Date().toISOString(),

    pending: false,
  };
}

/* --------------------------------------------------------------------------
 * GET /chat/{session_id}/history
 * -------------------------------------------------------------------------- */

export async function getChatHistory(sessionId) {
  if (sessionId == null) {
    return [];
  }

  try {
    const response = await api.get(
      `/chat/${sessionId}/history`
    );

    const history = Array.isArray(response.data)
      ? response.data
      : [];

    return history.map(normalizeHistoryMessage);
  } catch (error) {
    throw toFriendlyError(error);
  }
}

/* --------------------------------------------------------------------------
 * POST /chat
 *
 * body:
 * {
 *   session_id,
 *   message
 * }
 * -------------------------------------------------------------------------- */

export async function sendMessage(sessionId, message) {
  if (sessionId == null) {
    throw new Error("No active conversation selected.");
  }

  const trimmedMessage = String(message ?? "").trim();

  if (!trimmedMessage) {
    throw new Error("Please enter a message.");
  }

  try {
    const response = await api.post("/chat", {
      session_id: sessionId,
      message: trimmedMessage,
    });

    return normalizeChatResponse(response.data);
  } catch (error) {
    throw toFriendlyError(error);
  }
}

/* --------------------------------------------------------------------------
 * POST /chat/{session_id}/resume
 *
 * body:
 * {
 *   value
 * }
 *
 * This is used when ORCA is waiting for additional information,
 * such as:
 *
 *   "Please provide your fishing location."
 *
 * The user still types the answer in the normal chat composer.
 * The UI does NOT display backend options as clickable buttons.
 * -------------------------------------------------------------------------- */

export async function resumeChat(sessionId, value) {
  if (sessionId == null) {
    throw new Error("No active conversation selected.");
  }

  if (value == null || (typeof value === "string" && !value.trim())) {
    throw new Error("Please enter a value.");
  }

  try {
    const response = await api.post(
      `/chat/${sessionId}/resume`,
      {
        value,
      }
    );

    return normalizeChatResponse(response.data);
  } catch (error) {
    throw toFriendlyError(error);
  }
}