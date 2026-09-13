/* ============================================================================
 * chatApi.js — chat MESSAGE service (mock layer)
 * ============================================================================
 * Scope: conversation/message endpoints only. Session CRUD belongs to the
 * teammate's session layer and is NOT here.
 *
 * NO NETWORK CALLS. Everything is local/in-memory with simulated latency.
 *
 * Real contract (already live):
 *   POST /chat                          { session_id, message } -> { message }
 *   GET  /chat/{session_id}/history      -> [{ id, role, content, response_data }]
 * Real contract (coming later):
 *   PUT  /chat/{session_id}/messages/{message_id}
 *   POST /chat/{session_id}/regenerate
 *   POST /chat/{session_id}/feedback
 *   GET  /chat/suggestions
 * ==========================================================================*/

const MOCK_LATENCY_MS = 700;

function delay(ms = MOCK_LATENCY_MS) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

let idCounter = 0;
function makeId() {
  idCounter += 1;
  return `local-${Date.now()}-${idCounter}`;
}

const conversationStore = new Map();

const CANNED_REPLIES = [
  {
    match: /pfz|fishing zone/i,
    content:
      "There are two potential fishing zones (PFZ) within range, both showing favorable chlorophyll and temperature gradients for the next 24 hours.",
    response_data: {
      type: "pfz",
      summary: "2 zones identified within range",
      fields: [
        { label: "Zone A", value: "18 nm NE — high confidence" },
        { label: "Zone B", value: "27 nm ESE — moderate confidence" },
      ],
    },
  },
  {
    match: /route|voyage|kanyakumari|travel/i,
    content:
      "Here's a suggested route based on current conditions. It avoids the restricted zone to the south and stays within safe wave-height limits for most of the passage.",
    response_data: {
      type: "route",
      summary: "1 recommended route, 2 alternates",
      fields: [
        { label: "Distance", value: "142 nm" },
        { label: "Estimated duration", value: "9h 40m" },
        { label: "Risk level", value: "Low" },
      ],
    },
  },
  {
    match: /risk|safe|danger|storm/i,
    content:
      "Current risk assessment is low to moderate. There's a developing weather system further offshore, but it isn't expected to affect coastal waters in your window.",
    response_data: {
      type: "risk",
      summary: "Low–moderate risk in your window",
      fields: [
        { label: "Overall risk", value: "Low–moderate" },
        { label: "Primary factor", value: "Offshore system (monitor)" },
      ],
    },
  },
  {
    match: /weather|wind|wave|condition/i,
    content:
      "Tomorrow's marine conditions appear moderately favorable. Wind and wave conditions should be monitored before departure.",
    response_data: {
      type: "weather",
      summary: "Moderately favorable, monitor before departure",
      fields: [
        { label: "Wind speed", value: "13 kt, NE" },
        { label: "Wave height", value: "0.7 – 1.1 m" },
      ],
    },
  },
];

const FALLBACK_REPLIES = [
  "Based on the available marine conditions, things look moderately favorable — but I'd recommend confirming wind and wave data closer to departure.",
  "I've reviewed the closest available marine data for that. Conditions are within normal range, with no major advisories currently active.",
  "That falls within a manageable risk range right now. I'd suggest a final check on local conditions a few hours before you head out.",
];

function pickReply(userMessage) {
  const match = CANNED_REPLIES.find((entry) => entry.match.test(userMessage));
  if (match) return { content: match.content, response_data: match.response_data };
  const content = FALLBACK_REPLIES[Math.floor(Math.random() * FALLBACK_REPLIES.length)];
  return { content, response_data: null };
}

function getStore(sessionId) {
  const key = sessionId ?? "__standalone__";
  if (!conversationStore.has(key)) conversationStore.set(key, []);
  return conversationStore.get(key);
}

export async function getChatHistory(sessionId) {
  await delay(400);
  return [...getStore(sessionId)];
}

export async function sendMessage(sessionId, message) {
  await delay();

  if (message.trim().toLowerCase() === "trigger error") {
    throw { message: "ORCA couldn't complete that request." };
  }

  const store = getStore(sessionId);
  const userMessage = {
    id: makeId(),
    role: "user",
    content: message,
    response_data: null,
    created_at: new Date().toISOString(),
  };
  const { content, response_data } = pickReply(message);
  const assistantMessage = {
    id: makeId(),
    role: "assistant",
    content,
    response_data,
    created_at: new Date().toISOString(),
  };
  store.push(userMessage, assistantMessage);
  return assistantMessage;
}

export async function editMessage(sessionId, messageId, content) {
  await delay();
  const store = getStore(sessionId);
  const index = store.findIndex((m) => m.id === messageId);
  if (index === -1) throw { message: "That message no longer exists." };

  const editedMessage = { ...store[index], content, created_at: new Date().toISOString() };
  const { content: replyContent, response_data } = pickReply(content);
  const assistantMessage = {
    id: makeId(),
    role: "assistant",
    content: replyContent,
    response_data,
    created_at: new Date().toISOString(),
  };

  const key = sessionId ?? "__standalone__";
  const newStore = [...store.slice(0, index), editedMessage, assistantMessage];
  conversationStore.set(key, newStore);
  return { messages: newStore };
}

export async function regenerateMessage(sessionId, messageId) {
  await delay();
  const store = getStore(sessionId);
  const index = store.findIndex((m) => m.id === messageId);
  if (index === -1) throw { message: "That message no longer exists." };

  const precedingUserMessage = store
    .slice(0, index)
    .reverse()
    .find((m) => m.role === "user");
  const { content, response_data } = pickReply(precedingUserMessage?.content ?? "");
  const regenerated = { ...store[index], content, response_data, created_at: new Date().toISOString() };
  store[index] = regenerated;
  return regenerated;
}

export async function sendFeedback(sessionId, messageId, feedback) {
  await delay(250);
  const store = getStore(sessionId);
  const index = store.findIndex((m) => m.id === messageId);
  if (index !== -1) store[index] = { ...store[index], feedback };
  return { messageId, feedback };
}

export async function getSuggestions() {
  await delay(300);
  return [
    "What are today's fishing conditions?",
    "Show nearby PFZ locations",
    "Is it safe to fish tomorrow?",
    "Find a safer route for my voyage",
  ];
}