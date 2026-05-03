"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { Send, Bot, User, AlertTriangle, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import api from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  guardrail_triggered: boolean;
  latency_ms: number | null;
  created_at: string;
}

interface MessageListResponse {
  items: Message[];
  total: number;
  page: number;
  limit: number;
}

interface Conversation {
  id: string;
  channel: string;
  status: string;
  language: string;
  lead_id: string | null;
}

export default function ChatPage() {
  const params = useParams<{ id: string }>();
  const conversationId = params.id;

  const [conv, setConv] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Load conversation + messages
  useEffect(() => {
    if (!conversationId) return;
    api.get<Conversation>(`/api/v1/conversations/${conversationId}`).then((r) => setConv(r.data));
    api
      .get<MessageListResponse>(`/api/v1/conversations/${conversationId}/messages?limit=100`)
      .then((r) => setMessages(r.data.items));
  }, [conversationId]);

  // Scroll to bottom on new message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || sending) return;

    setInput("");
    setSending(true);
    setError(null);

    // Optimistic user message
    const tempId = `temp-${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      {
        id: tempId,
        role: "user",
        content: text,
        guardrail_triggered: false,
        latency_ms: null,
        created_at: new Date().toISOString(),
      },
    ]);

    try {
      const resp = await api.post<Message>(`/api/v1/conversations/${conversationId}/messages`, {
        content: text,
        language: conv?.language ?? "en",
        attachments: [],
      });

      // Replace temp + add assistant response
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== tempId),
        {
          id: `user-${Date.now()}`,
          role: "user" as const,
          content: text,
          guardrail_triggered: false,
          latency_ms: null,
          created_at: new Date().toISOString(),
        },
        resp.data,
      ]);
    } catch {
      setError("Failed to send message. Please try again.");
      setMessages((prev) => prev.filter((m) => m.id !== tempId));
    } finally {
      setSending(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] -mx-6 -mb-6">
      {/* Header */}
      <div className="flex items-center gap-4 px-6 py-4 bg-white border-b border-gray-200 shrink-0">
        <Link href="/admin/conversations" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-base font-semibold text-gray-900">
            Conversation
          </h1>
          <p className="text-xs text-gray-500">
            {conv ? `${conv.channel} · ${conv.status} · ${conv.language.toUpperCase()}` : "Loading…"}
          </p>
        </div>
        {conv?.status === "handoff" && (
          <span className="ml-auto flex items-center gap-1.5 px-3 py-1 bg-orange-50 text-orange-700 rounded-full text-xs font-medium">
            <AlertTriangle className="h-3 w-3" />
            Handoff Requested
          </span>
        )}
      </div>

      {/* Message list */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-gray-50">
        {messages.length === 0 && (
          <p className="text-center text-sm text-gray-400 mt-12">No messages yet.</p>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} msg={msg} />
        ))}
        {sending && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Error banner */}
      {error && (
        <div className="px-6 py-2 bg-red-50 border-t border-red-100 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Input bar */}
      <div className="px-6 py-4 bg-white border-t border-gray-200 shrink-0">
        <div className="flex gap-3 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            rows={1}
            placeholder="Type a message… (Enter to send)"
            className="flex-1 resize-none border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 max-h-32 overflow-y-auto"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || sending}
            className="p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === "user";
  return (
    <div className={cn("flex gap-3", isUser ? "flex-row-reverse" : "flex-row")}>
      <div
        className={cn(
          "h-8 w-8 rounded-full shrink-0 flex items-center justify-center",
          isUser ? "bg-blue-100" : "bg-gray-200"
        )}
      >
        {isUser ? (
          <User className="h-4 w-4 text-blue-600" />
        ) : (
          <Bot className="h-4 w-4 text-gray-600" />
        )}
      </div>
      <div className={cn("max-w-[70%] space-y-1", isUser ? "items-end" : "items-start", "flex flex-col")}>
        <div
          className={cn(
            "px-4 py-2.5 rounded-2xl text-sm leading-relaxed",
            isUser
              ? "bg-blue-600 text-white rounded-tr-sm"
              : "bg-white border border-gray-200 text-gray-800 rounded-tl-sm"
          )}
        >
          {msg.content}
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span>
            {new Date(msg.created_at).toLocaleTimeString("en-AE", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
          {msg.guardrail_triggered && (
            <span className="text-orange-500 flex items-center gap-0.5">
              <AlertTriangle className="h-3 w-3" />
              Guardrail
            </span>
          )}
          {msg.latency_ms && <span>{msg.latency_ms}ms</span>}
        </div>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center">
        <Bot className="h-4 w-4 text-gray-600" />
      </div>
      <div className="bg-white border border-gray-200 px-4 py-2.5 rounded-2xl rounded-tl-sm">
        <span className="flex gap-1 items-center h-4">
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
  );
}
