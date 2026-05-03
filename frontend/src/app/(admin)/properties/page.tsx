"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Building2, Search, Filter, Plus } from "lucide-react";
import api from "@/lib/api";

interface Property {
  id: string;
  title: string;
  property_type: string;
  status: string;
  purpose: string;
  price_aed: number | null;
  bedrooms: number | null;
  area_sqft: number | null;
  address: string | null;
  is_off_plan: boolean;
  is_freehold: boolean;
  slug: string | null;
  created_at: string;
}

interface PropertyListResponse {
  items: Property[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

const PROPERTY_TYPE_LABELS: Record<string, string> = {
  apartment: "Apartment",
  villa: "Villa",
  townhouse: "Townhouse",
  penthouse: "Penthouse",
  studio: "Studio",
  office: "Office",
};

const STATUS_COLORS: Record<string, string> = {
  available: "bg-green-100 text-green-700",
  off_plan: "bg-blue-100 text-blue-700",
  reserved: "bg-yellow-100 text-yellow-700",
  sold: "bg-red-100 text-red-700",
  rented: "bg-purple-100 text-purple-700",
};

export default function PropertiesPage() {
  const [data, setData] = useState<PropertyListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);

  const fetchProperties = (query: string, p: number) => {
    setLoading(true);
    const params = new URLSearchParams({ page: String(p), limit: "20" });
    if (query) params.set("q", query);

    api
      .get<PropertyListResponse>(`/api/v1/properties/search?${params}`)
      .then((res) => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchProperties(q, page);
  }, [page]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchProperties(q, 1);
  };

  const formatPrice = (price: number | null, purpose: string) => {
    if (!price) return "POA";
    if (purpose === "rent") return `AED ${price.toLocaleString()}/yr`;
    return `AED ${(price / 1_000_000).toFixed(2)}M`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Properties</h1>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
          <Plus className="h-4 w-4" />
          Add Property
        </button>
      </div>

      {/* Search bar */}
      <form onSubmit={handleSearch} className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search properties by title, area, description…"
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          type="submit"
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 flex items-center gap-2"
        >
          <Filter className="h-4 w-4" />
          Search
        </button>
      </form>

      {/* Stats */}
      {data && (
        <p className="text-sm text-gray-500">
          {data.total} propert{data.total === 1 ? "y" : "ies"} found
        </p>
      )}

      {/* Property grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-48 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data?.items.map((prop) => (
              <div
                key={prop.id}
                className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow overflow-hidden"
              >
                {/* Image placeholder */}
                <div className="h-36 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                  <Building2 className="h-10 w-10 text-gray-400" />
                </div>

                <div className="p-4 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-semibold text-gray-900 text-sm leading-tight line-clamp-2">
                      {prop.title}
                    </h3>
                    <span
                      className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-medium ${
                        STATUS_COLORS[prop.status] ?? "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {prop.status.replace("_", " ")}
                    </span>
                  </div>

                  <p className="text-xs text-gray-500 truncate">{prop.address || "Dubai, UAE"}</p>

                  <div className="flex items-center justify-between pt-1">
                    <span className="text-sm font-bold text-blue-700">
                      {formatPrice(prop.price_aed, prop.purpose)}
                    </span>
                    <span className="text-xs text-gray-500">
                      {PROPERTY_TYPE_LABELS[prop.property_type] ?? prop.property_type}
                      {prop.bedrooms ? ` · ${prop.bedrooms}BR` : ""}
                    </span>
                  </div>

                  <div className="flex gap-2 pt-1">
                    {prop.is_freehold && (
                      <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded text-xs">
                        Freehold
                      </span>
                    )}
                    {prop.is_off_plan && (
                      <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded text-xs">
                        Off-Plan
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Empty state */}
          {data?.items.length === 0 && (
            <div className="text-center py-16 text-gray-400">
              <Building2 className="h-12 w-12 mx-auto mb-3 opacity-40" />
              <p className="text-sm">No properties found.</p>
            </div>
          )}

          {/* Pagination */}
          {data && data.pages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-4">
              <button
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
                className="px-3 py-1 text-sm border rounded-md disabled:opacity-40 hover:bg-gray-50"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600">
                Page {data.page} of {data.pages}
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
        </>
      )}
    </div>
  );
}
