"use client";

import { useEffect, useState } from "react";
import { Calendar, Clock, MapPin } from "lucide-react";
import { cn } from "@/lib/utils";
import api from "@/lib/api";

interface Appointment {
  id: string;
  title: string;
  type: string;
  status: string;
  start_time: string;
  end_time: string;
  location: string | null;
  lead_id: string | null;
  agent_id: string | null;
  property_id: string | null;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700",
  confirmed: "bg-green-100 text-green-700",
  cancelled: "bg-red-100 text-red-700",
  completed: "bg-blue-100 text-blue-700",
  no_show: "bg-gray-100 text-gray-600",
};

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<Appointment[]>("/api/v1/appointments?limit=50")
      .then((r) => setAppointments(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const formatDateTime = (iso: string) =>
    new Date(iso).toLocaleString("en-AE", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

  const formatDuration = (start: string, end: string) => {
    const mins = Math.round((new Date(end).getTime() - new Date(start).getTime()) / 60000);
    return `${mins} min`;
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Appointments</h1>

      {loading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : appointments.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <Calendar className="h-10 w-10 mx-auto mb-2 opacity-40" />
          <p className="text-sm">No appointments scheduled.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {appointments.map((appt) => (
            <div
              key={appt.id}
              className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex items-start gap-4"
            >
              <div className="h-12 w-12 rounded-lg bg-blue-50 flex flex-col items-center justify-center shrink-0">
                <span className="text-xs font-semibold text-blue-600">
                  {new Date(appt.start_time).toLocaleDateString("en-AE", { month: "short" })}
                </span>
                <span className="text-lg font-bold text-blue-700 leading-none">
                  {new Date(appt.start_time).getDate()}
                </span>
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-semibold text-gray-900 truncate">{appt.title}</h3>
                  <span
                    className={cn(
                      "shrink-0 px-2.5 py-0.5 rounded-full text-xs font-medium capitalize",
                      STATUS_COLORS[appt.status] ?? "bg-gray-100 text-gray-600"
                    )}
                  >
                    {appt.status}
                  </span>
                </div>

                <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatDateTime(appt.start_time)} · {formatDuration(appt.start_time, appt.end_time)}
                  </span>
                  {appt.location && (
                    <span className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {appt.location}
                    </span>
                  )}
                  <span className="capitalize text-gray-400">{appt.type.replace("_", " ")}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
