"use client";

import { useEffect, useState } from "react";
import { MessageSquare, CheckCircle, AlertTriangle, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import api from "@/lib/api";

interface Conversation {
  id: string;
  channel: string;
  status: string;
  language: string;
  lead_id: string | null;
  created_at: string;
  updated_at: string;
}

const STATUS_CONFIG: Record<string, { label: string; icon: React.ElementType; color: string }> = {
  active: { label: "Active", icon: MessageSquare, color: "text-blue-600 bg-blue-50" },
  resolved: { label: "Resolved", icon: CheckCircle, color: "text-green-600 bg-green-50" },
  handoff: { label: "Handoff", icon: AlertTriangle, color: "text-orange-600 bg-orange-50" },
  abandoned: { label: "Abandoned", icon: Clock, color: "text-gray-500 bg-gray-50" },
};

const CHANNEL_LABELS: Record<string, string> = {
  web: "Web Chat",
  whatsapp: "WhatsApp",
  telegram: "Telegram",
};

const LANG_FLAGS: Record<string, string> = {
  en: "🇬🇧",
  ar: "🇦🇪",
  hi: "🇮🇳",
  ru: "🇷🇺",
};

type StatusFilter = "all" | "active" | "resolved" | "handoff" | "abandoned";

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");

  const fetch = (filter: StatusFilter) => {
    setLoading(true);
    const params = new URLSearchParams({ limit: "50" });
    if (filter !== "all") params.set("status", filter);
    api
      .get<Conversation[]>(`/api/v1/conversations?${params}`)
      .then((res) => setConversations(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetch(statusFilter);
  }, [statusFilter]);

  const formatDate = (iso: string) =>
    new Date(iso).toLocaleString("en-AE", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Conversations</h1>

      {/* Status filter tabs */}
      <div className="flex gap-2 border-b border-gray-200 pb-0">
        {(["all", "active", "handoff", "resolved", "abandoned"] as StatusFilter[]).map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={cn(
              "px-4 py-2 text-sm font-medium border-b-2 -mb-px capitalize transition-colors",
              statusFilter === s
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            )}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="space-y-0 divide-y divide-gray-100">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-50 animate-pulse" />
            ))}
          </div>
        ) : conversations.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <MessageSquare className="h-10 w-10 mx-auto mb-2 opacity-40" />
            <p className="text-sm">No conversations found.</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Channel</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Status</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Language</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Lead</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Last Activity</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {conversations.map((conv) => {
                const statusCfg = STATUS_CONFIG[conv.status] ?? STATUS_CONFIG.active;
                const StatusIcon = statusCfg.icon;
                return (
                  <tr key={conv.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <span className="font-medium text-gray-700">
                        {CHANNEL_LABELS[conv.channel] ?? conv.channel}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={cn(
                          "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium",
                          statusCfg.color
                        )}
                      >
                        <StatusIcon className="h-3 w-3" />
                        {statusCfg.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {LANG_FLAGS[conv.language] ?? ""} {conv.language.toUpperCase()}
                    </td>
                    <td className="px-4 py-3 text-gray-500 font-mono text-xs">
                      {conv.lead_id ? conv.lead_id.slice(0, 8) + "…" : "—"}
                    </td>
                    <td className="px-4 py-3 text-gray-500">{formatDate(conv.updated_at)}</td>
                    <td className="px-4 py-3">
                      <a
                        href={`/admin/chat/${conv.id}`}
                        className="text-blue-600 hover:text-blue-800 text-xs font-medium"
                      >
                        Open
                      </a>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
