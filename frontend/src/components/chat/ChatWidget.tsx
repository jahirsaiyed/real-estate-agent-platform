"use client";

/**
 * ChatWidget — embeddable AI chat widget.
 *
 * Usage (embed on any site):
 *   <script src="https://your-domain.com/widget.js" data-tenant-id="xxx"></script>
 *
 * Or use directly inside Next.js pages:
 *   import { ChatWidget } from "@/components/chat/ChatWidget";
 *   <ChatWidget tenantId="xxx" apiBase="https://api.example.com" />
 */

import { useEffect, useRef, useState } from "react";
import { MessageSquare, X, Send, Bot, User, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  searchResults?: PropertyResult[];
}

interface PropertyResult {
  id: string;
  title: string;
  price_aed: number | null;
  bedrooms: number | null;
  address: string | null;
}

interface ChatWidgetProps {
  tenantId?: string;
  apiBase?: string;
  primaryColor?: string;
  agentName?: string;
  greeting?: string;
  conversationId?: string;
}

const API_BASE =
  typeof window !== "undefined"
    ? window.location.origin.includes("localhost")
      ? "http://localhost:8000"
      : ""
    : "";

export function ChatWidget({
  apiBase = API_BASE,
  agentName = "Layla",
  greeting = "Hello! I'm Layla, your Dubai real estate specialist. How can I help you today?",
  conversationId: initialConvId,
}: ChatWidgetProps) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [convId, setConvId] = useState<string | null>(initialConvId ?? null);
  const [unread, setUnread] = useState(0);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Greeting message
  useEffect(() => {
    setMessages([
      {
        id: "greeting",
        role: "assistant",
        content: greeting,
        timestamp: new Date(),
      },
    ]);
  }, [greeting]);

  // Auto-scroll
  useEffect(() => {
    if (open) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
      setUnread(0);
    }
  }, [messages, open]);

  // Focus input on open
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [open]);

  const ensureConversation = async (): Promise<string> => {
    if (convId) return convId;
    const res = await fetch(`${apiBase}/api/v1/conversations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ channel: "web", language: "en" }),
    });
    if (!res.ok) throw new Error("Failed to create conversation");
    const data = await res.json();
    setConvId(data.id);
    return data.id;
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const cid = await ensureConversation();
      const res = await fetch(`${apiBase}/api/v1/conversations/${cid}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: text, language: "en", attachments: [] }),
      });

      if (!res.ok) throw new Error("Request failed");
      const data = await res.json();

      const assistantMsg: ChatMessage = {
        id: data.id ?? `asst-${Date.now()}`,
        role: "assistant",
        content: data.content,
        timestamp: new Date(data.created_at),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      if (!open) setUnread((n) => n + 1);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: "assistant",
          content: "I'm having a moment. Please try again shortly.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* Chat panel */}
      <div
        className={cn(
          "fixed bottom-20 right-4 z-50 w-80 sm:w-96 flex flex-col shadow-2xl rounded-2xl overflow-hidden border border-gray-200 bg-white transition-all duration-300",
          open ? "opacity-100 translate-y-0 pointer-events-auto" : "opacity-0 translate-y-4 pointer-events-none"
        )}
        style={{ maxHeight: "70vh", height: "500px" }}
      >
        {/* Header */}
        <div className="flex items-center gap-3 px-4 py-3 bg-blue-600 text-white shrink-0">
          <div className="h-8 w-8 rounded-full bg-white/20 flex items-center justify-center">
            <Bot className="h-4 w-4" />
          </div>
          <div className="flex-1">
            <p className="font-semibold text-sm">{agentName}</p>
            <p className="text-xs text-blue-200">Dubai Real Estate Specialist</p>
          </div>
          <button
            onClick={() => setOpen(false)}
            className="p-1 rounded-full hover:bg-white/20 transition-colors"
          >
            <ChevronDown className="h-4 w-4" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
          {messages.map((msg) => (
            <WidgetMessage key={msg.id} msg={msg} />
          ))}
          {loading && (
            <div className="flex gap-2">
              <div className="h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                <Bot className="h-3 w-3 text-blue-600" />
              </div>
              <div className="bg-white border border-gray-200 px-3 py-2 rounded-2xl rounded-tl-sm">
                <span className="flex gap-1">
                  {[0, 1, 2].map((i) => (
                    <span
                      key={i}
                      className="h-1.5 w-1.5 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: `${i * 0.15}s` }}
                    />
                  ))}
                </span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="px-3 py-3 bg-white border-t border-gray-100 shrink-0">
          <div className="flex gap-2 items-end">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              rows={1}
              placeholder="Ask about properties in Dubai…"
              className="flex-1 resize-none border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 max-h-24 overflow-y-auto"
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              className="p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-40 transition-colors shrink-0"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
          <p className="text-center text-xs text-gray-300 mt-1.5">
            Powered by Sceptre Estate AI
          </p>
        </div>
      </div>

      {/* FAB button */}
      <button
        onClick={() => setOpen((o) => !o)}
        className="fixed bottom-4 right-4 z-50 h-14 w-14 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 transition-all duration-200 hover:scale-105 flex items-center justify-center"
        aria-label="Open chat"
      >
        {open ? (
          <X className="h-6 w-6" />
        ) : (
          <>
            <MessageSquare className="h-6 w-6" />
            {unread > 0 && (
              <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center font-bold">
                {unread > 9 ? "9+" : unread}
              </span>
            )}
          </>
        )}
      </button>
    </>
  );
}

function WidgetMessage({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user";
  return (
    <div className={cn("flex gap-2", isUser ? "flex-row-reverse" : "flex-row")}>
      <div
        className={cn(
          "h-6 w-6 rounded-full shrink-0 flex items-center justify-center mt-0.5",
          isUser ? "bg-blue-100" : "bg-blue-600"
        )}
      >
        {isUser ? (
          <User className="h-3 w-3 text-blue-600" />
        ) : (
          <Bot className="h-3 w-3 text-white" />
        )}
      </div>
      <div
        className={cn(
          "px-3 py-2 rounded-2xl text-sm max-w-[80%] leading-relaxed",
          isUser
            ? "bg-blue-600 text-white rounded-tr-sm"
            : "bg-white border border-gray-200 text-gray-800 rounded-tl-sm"
        )}
      >
        {msg.content}
      </div>
    </div>
  );
}
