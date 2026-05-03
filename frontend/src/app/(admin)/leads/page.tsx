"use client";

import { useEffect, useState } from "react";
import { Users, Star } from "lucide-react";
import { cn } from "@/lib/utils";
import api from "@/lib/api";

interface Lead {
  id: string;
  full_name: string | null;
  phone: string | null;
  email: string | null;
  nationality: string | null;
  language: string;
  qualification_score: number;
  qualification_status: string;
  source_channel: string;
  created_at: string;
  updated_at: string;
}

interface LeadListResponse {
  items: Lead[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

const STATUS_COLORS: Record<string, string> = {
  unqualified: "bg-gray-100 text-gray-600",
  in_progress: "bg-yellow-100 text-yellow-700",
  qualified: "bg-green-100 text-green-700",
  handoff: "bg-orange-100 text-orange-700",
};

const CHANNEL_LABELS: Record<string, string> = {
  web: "Web",
  whatsapp: "WhatsApp",
  telegram: "Telegram",
};

type QualFilter = "all" | "unqualified" | "in_progress" | "qualified" | "handoff";

export default function LeadsPage() {
  const [data, setData] = useState<LeadListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<QualFilter>("all");
  const [page, setPage] = useState(1);

  const fetchLeads = (f: QualFilter, p: number) => {
    setLoading(true);
    const params = new URLSearchParams({ page: String(p), limit: "20" });
    if (f !== "all") params.set("qualification_status", f);
    api
      .get<LeadListResponse>(`/api/v1/leads?${params}`)
      .then((r) => setData(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchLeads(filter, page);
  }, [filter, page]);

  const scoreColor = (score: number) => {
    if (score >= 70) return "text-green-600";
    if (score >= 40) return "text-yellow-600";
    return "text-gray-400";
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Leads</h1>
        {data && (
          <span className="text-sm text-gray-500">{data.total} total leads</span>
        )}
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 border-b border-gray-200">
        {(["all", "qualified", "in_progress", "handoff", "unqualified"] as QualFilter[]).map((f) => (
          <button
            key={f}
            onClick={() => { setFilter(f); setPage(1); }}
            className={cn(
              "px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors capitalize",
              filter === f
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            )}
          >
            {f.replace("_", " ")}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="divide-y divide-gray-100">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-50 animate-pulse" />
            ))}
          </div>
        ) : data?.items.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <Users className="h-10 w-10 mx-auto mb-2 opacity-40" />
            <p className="text-sm">No leads found.</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Name</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Contact</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Score</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Status</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Channel</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data?.items.map((lead) => (
                <tr key={lead.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium text-gray-900">
                        {lead.full_name || "Anonymous"}
                      </p>
                      <p className="text-xs text-gray-400 font-mono">{lead.id.slice(0, 8)}…</p>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    <div>
                      {lead.phone && <p>{lead.phone}</p>}
                      {lead.email && <p className="text-xs">{lead.email}</p>}
                      {!lead.phone && !lead.email && <span className="text-gray-300">—</span>}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={cn("font-bold", scoreColor(lead.qualification_score))}>
                      {lead.qualification_score}/80
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={cn(
                        "px-2.5 py-1 rounded-full text-xs font-medium capitalize",
                        STATUS_COLORS[lead.qualification_status] ?? "bg-gray-100 text-gray-600"
                      )}
                    >
                      {lead.qualification_status.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {CHANNEL_LABELS[lead.source_channel] ?? lead.source_channel}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(lead.created_at).toLocaleDateString("en-AE", {
                      month: "short",
                      day: "numeric",
                    })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="px-3 py-1 text-sm border rounded-md disabled:opacity-40 hover:bg-gray-50"
          >
            Previous
          </button>
          <span className="text-sm text-gray-600">
            {data.page} / {data.pages}
          </span>
          <button
            disabled={page === data.pages}
            onClick={() => setPage((p) => p + 1)}
            className="px-3 py-1 text-sm border rounded-md disabled:opacity-40 hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
