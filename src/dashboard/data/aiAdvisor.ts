/**
 * AI Advisor — frontend chat service.
 *
 * `sendMessageToAI()` is the single seam between the UI and the "AI".
 * The UI does not need to know how the AI works.
 *
 * The frontend sends the farmer's question to the KisanSetu
 * backend AI endpoint. API keys stay on the backend.
 */

export type ChatRole = "ai" | "user";

export interface ChatMessage {
  id: string;
  role: ChatRole;

  /** Message text — `**bold**` segments render as strong. */
  text: string;

  time: string;

  /** Suggested follow-up buttons rendered under this message (AI only). */
  related?: string[];

  /** Renders the "You can try asking" suggestion block under this message. */
  showSuggestions?: boolean;
}

export interface AIResponse {
  text: string;
  related?: string[];
}

/** The four starter suggestions shown in the reference. */
export const SUGGESTED_QUESTIONS = [
  "Best crop for my area",
  "Today's market price of tomato",
  "How to control pests?",
  "Weather forecast for this week",
];

export function nowTime(): string {
  return new Date().toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

/** Seed conversation from the reference (UI seed data — no DB collection). */
export function seedConversation(firstName: string): ChatMessage[] {
  return [
    {
      id: "m1",
      role: "ai",
      text: `Hello ${firstName}! 👋\n\nI'm KisanSetu AI, your farming assistant.\nHow can I help you today?`,
      time: "10:24 AM",
      showSuggestions: true,
    },
    {
      id: "m2",
      role: "user",
      text: "What is the current market price of onion in Nashik?",
      time: "10:25 AM",
    },
    {
      id: "m3",
      role: "ai",
      text: "The current market price of onion in Nashik Mandi is\n**₹ 1,800 – ₹ 2,200 per quintal** (for **Grade A**).\n\nPrices may vary based on quality and demand.",
      time: "10:25 AM",
      related: [
        "Show price trend of onion",
        "Best time to sell onion",
        "Onion storage tips",
      ],
    },
  ];
}

/* ------------------------- Real AI backend -------------------------------- */

const AI_API_URL = "http://127.0.0.1:8000";

type BackendChatResponse = {
  response?: string;
  text?: string;
  message?: string;
  answer?: string;
};

export interface FarmerContextForAI {
  firstName: string;
  location: string;
  language?: string;
}

/**
 * Creates one conversation ID for the current browser session.
 *
 * This allows the backend AI to keep the conversation context.
 */
function getConversationId(): string {
  const key = "kisansetu.ai.conversation_id";

  const existing = sessionStorage.getItem(key);

  if (existing) {
    return existing;
  }

  const id = `frontend_${Date.now()}_${Math.random()
    .toString(36)
    .slice(2, 10)}`;

  sessionStorage.setItem(key, id);

  return id;
}

/**
 * Sends the farmer's question to the real KisanSetu AI backend.
 *
 * The frontend does NOT communicate directly with Claude/MCP.
 * API keys remain on the backend.
 */
export async function sendMessageToAI(
  message: string,
  ctx: FarmerContextForAI
): Promise<AIResponse> {
  const text = message.trim();

  if (!text) {
    return {
      text: "Please enter a question.",
    };
  }

  try {
    const response = await fetch(`${AI_API_URL}/ai/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        conversation_id: getConversationId(),
        message: text,
        language: ctx.language || "English",
        location: ctx.location,
      }),
    });

    if (!response.ok) {
      throw new Error(
        `AI backend returned HTTP ${response.status}`
      );
    }

    const data = (await response.json()) as BackendChatResponse;

    const aiText =
      data.response ||
      data.text ||
      data.message ||
      data.answer;

    if (!aiText) {
      throw new Error("AI backend returned an empty response.");
    }

    return {
      text: aiText,
    };
  } catch (error) {
    console.error("KisanSetu AI request failed:", error);

    return {
      text:
        "I'm unable to connect to the KisanSetu AI service right now. Please make sure the AI backend is running and try again.",
    };
  }
}