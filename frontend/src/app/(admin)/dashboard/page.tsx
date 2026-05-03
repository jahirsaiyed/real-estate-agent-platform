"use client";

import { useEffect, useState } from "react";
import { Users, MessageSquare, Building2, Calendar, TrendingUp } from "lucide-react";
import api from "@/lib/api";

interface ServiceStatus {
  status: string;
  detail?: string;
}

interface ReadinessData {
  status: string;
  services: Record<string, ServiceStatus>;
}

interface Stats {
  leads: number;
  conversations: number;
  properties: number;
  appointments: number;
}

const SERVICE_LABELS: Record<string, string> = {
  database: "PostgreSQL",
  redis: "Redis",
  qdrant: "Qdrant (Vector DB)",
};

export default function DashboardPage() {
  const [readiness, setReadiness] = useState<ReadinessData | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [healthRes, leadsRes, convsRes, propsRes, apptsRes] = await Promise.allSettled([
          api.get<ReadinessData>("/api/v1/health/ready"),
          api.get<{ total: number }>("/api/v1/leads?limit=1"),
          api.get<{ length: number }>("/api/v1/conversations?limit=1&status=active"),
          api.get<{ total: number }>("/api/v1/properties/search?limit=1"),
          api.get<unknown[]>("/api/v1/appointments?limit=1"),
        ]);

        if (healthRes.status === "fulfilled") setReadiness(healthRes.value.data);

        setStats({
          leads: leadsRes.status === "fulfilled" ? (leadsRes.value.data as { total: number }).total ?? 0 : 0,
          conversations: convsRes.status === "fulfilled"
            ? Array.isArray(convsRes.value.data) ? (convsRes.value.data as unknown[]).length : 0
            : 0,
          properties: propsRes.status === "fulfilled"
            ? (propsRes.value.data as { total: number }).total ?? 0
            : 0,
          appointments: apptsRes.status === "fulfilled"
            ? Array.isArray(apptsRes.value.data) ? (apptsRes.value.data as unknown[]).length : 0
            : 0,
        });
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const statCards = [
    {
      label: "Total Leads",
      value: stats?.leads ?? "—",
      icon: Users,
      color: "text-blue-600 bg-blue-50",
    },
    {
      label: "Active Conversations",
      value: stats?.conversations ?? "—",
      icon: MessageSquare,
      color: "text-purple-600 bg-purple-50",
    },
    {
      label: "Properties Listed",
      value: stats?.properties ?? "—",
      icon: Building2,
      color: "text-emerald-600 bg-emerald-50",
    },
    {
      label: "Upcoming Appointments",
      value: stats?.appointments ?? "—",
      icon: Calendar,
      color: "text-orange-600 bg-orange-50",
    },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map(({ label, value, icon: Icon, color }) => (
          <div
            key={label}
            className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm flex items-center gap-4"
          >
            <div className={`h-11 w-11 rounded-lg flex items-center justify-center ${color}`}>
              <Icon className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-gray-500 font-medium">{label}</p>
              <p className="mt-0.5 text-2xl font-bold text-gray-900">
                {loading ? <span className="text-gray-300">—</span> : value}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Service health */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="h-4 w-4 text-gray-500" />
          <h2 className="text-base font-semibold text-gray-900">Service Health</h2>
        </div>

        {loading && (
          <div className="space-y-2">
            {["database", "redis", "qdrant"].map((s) => (
              <div key={s} className="h-10 bg-gray-100 rounded animate-pulse" />
            ))}
          </div>
        )}

        {!loading && !readiness && (
          <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
            Could not reach backend.
          </div>
        )}

        {readiness && (
          <div className="space-y-2">
            {Object.entries(readiness.services).map(([key, svc]) => (
              <div
                key={key}
                className="flex items-center justify-between px-4 py-3 rounded-lg bg-gray-50 border border-gray-100"
              >
                <span className="text-sm font-medium text-gray-700">
                  {SERVICE_LABELS[key] ?? key}
                </span>
                <span
                  className={`text-sm font-semibold ${
                    svc.status === "connected" ? "text-green-600" : "text-red-500"
                  }`}
                >
                  {svc.status === "connected" ? "Connected" : svc.detail ?? "Error"}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
