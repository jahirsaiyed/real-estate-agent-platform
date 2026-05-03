"use client";

import { useEffect, useState } from "react";
import { Bot, Plus } from "lucide-react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

export default function ChatIndexPage() {
  const router = useRouter();
  const [creating, setCreating] = useState(false);

  const startNewChat = async () => {
    setCreating(true);
    try {
      const res = await api.post<{ id: string }>("/api/v1/conversations", {
        channel: "web",
        language: "en",
      });
      router.push(`/admin/chat/${res.data.id}`);
    } catch {
      setCreating(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-6">
      <div className="h-16 w-16 rounded-2xl bg-blue-50 flex items-center justify-center">
        <Bot className="h-8 w-8 text-blue-600" />
      </div>
      <div>
        <h2 className="text-xl font-bold text-gray-900">AI Chat</h2>
        <p className="text-sm text-gray-500 mt-1 max-w-xs">
          Start a new conversation with Layla, the Dubai real estate AI agent.
        </p>
      </div>
      <button
        onClick={startNewChat}
        disabled={creating}
        className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
      >
        <Plus className="h-4 w-4" />
        {creating ? "Starting…" : "New Conversation"}
      </button>
      <p className="text-xs text-gray-400">
        Or open an existing conversation from the{" "}
        <a href="/admin/conversations" className="text-blue-500 hover:underline">
          Conversations
        </a>{" "}
        page.
      </p>
    </div>
  );
}
