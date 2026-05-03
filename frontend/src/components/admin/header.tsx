"use client";

import { useRouter } from "next/navigation";
import { LogOut, User } from "lucide-react";
import { clearTokens } from "@/lib/auth";
import api from "@/lib/api";

export function Header() {
  const router = useRouter();

  async function handleLogout() {
    try {
      await api.post("/api/v1/auth/logout");
    } catch {
      // ignore errors — clear tokens regardless
    }
    clearTokens();
    router.push("/login");
  }

  return (
    <header className="fixed top-0 right-0 left-64 z-40 h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <div className="text-sm font-medium text-gray-700">Admin Panel</div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <User className="h-4 w-4" />
          <span>Admin</span>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-900 transition-colors"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </button>
      </div>
    </header>
  );
}
