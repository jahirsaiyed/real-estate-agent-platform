"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";

interface ServiceStatus {
  status: string;
  detail?: string;
}

interface ReadinessData {
  status: string;
  services: Record<string, ServiceStatus>;
}

const SERVICE_LABELS: Record<string, string> = {
  database: "PostgreSQL",
  redis: "Redis",
  qdrant: "Qdrant (Vector DB)",
};

const PLACEHOLDER_STATS = [
  { label: "Total Leads", value: "—" },
  { label: "Active Conversations", value: "—" },
  { label: "Properties Listed", value: "—" },
  { label: "Appointments Today", value: "—" },
];

export default function DashboardPage() {
  const [readiness, setReadiness] = useState<ReadinessData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<ReadinessData>("/api/v1/health/ready")
      .then((res) => setReadiness(res.data))
      .catch(() => setError("Could not reach backend"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      {/* Placeholder stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {PLACEHOLDER_STATS.map((stat) => (
          <div
            key={stat.label}
            className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm"
          >
            <p className="text-sm text-gray-500 font-medium">{stat.label}</p>
            <p className="mt-1 text-3xl font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Service health */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-4">Service Health</h2>

        {loading && (
          <div className="space-y-2">
            {["database", "redis", "qdrant"].map((s) => (
              <div key={s} className="h-10 bg-gray-100 rounded animate-pulse" />
            ))}
          </div>
        )}

        {error && (
          <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
        )}

        {readiness && (
          <div className="space-y-2">
            {Object.entries(readiness.services).map(([key, svc]) => (
              <div
                key={key}
                className="flex items-center justify-between px-4 py-3 rounded-md bg-gray-50 border border-gray-100"
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
