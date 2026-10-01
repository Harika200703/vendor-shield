import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  Building2,
  ChevronDown,
  Eye,
  Filter,
  Search,
  ShieldAlert,
  SlidersHorizontal,
  TrendingUp,
  X,
} from "lucide-react";
import { getVendors } from "../services/api";

const RISK_STYLES = {
  LOW: "border-emerald-200 bg-emerald-50 text-emerald-700",
  MEDIUM: "border-amber-200 bg-amber-50 text-amber-700",
  HIGH: "border-orange-200 bg-orange-50 text-orange-700",
  CRITICAL: "border-red-200 bg-red-50 text-red-700",
};

function normalizeRisk(value, score = 0) {
  const level = String(value || "").toUpperCase();
  if (RISK_STYLES[level]) return level;
  if (score >= 85) return "CRITICAL";
  if (score >= 70) return "HIGH";
  if (score >= 40) return "MEDIUM";
  return "LOW";
}

function formatCurrency(value) {
  const amount = Number(value || 0);
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatNumber(value) {
  return new Intl.NumberFormat("en-IN").format(Number(value || 0));
}

function getVendorId(vendor) {
  return vendor.vendor_id || vendor.id || vendor.vendorId;
}

function getVendorName(vendor) {
  return vendor.vendor_name || vendor.name || "Unknown Vendor";
}

function RiskBadge({ level }) {
  return (
    <span
      className={`inline-flex rounded-full border px-2.5 py-1 text-[10px] font-bold tracking-wide ${
        RISK_STYLES[level] || RISK_STYLES.LOW
      }`}
    >
      {level}
    </span>
  );
}

function StatCard({ label, value, icon: Icon, iconClass }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-slate-400">
            {label}
          </p>
          <p className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
            {value}
          </p>
        </div>
        <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${iconClass}`}>
          <Icon size={18} />
        </div>
      </div>
    </div>
  );
}

export default function Vendors() {
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [sortBy, setSortBy] = useState("risk");

  useEffect(() => {
    async function loadVendors() {
      try {
        setLoading(true);
        setError("");
        const response = await getVendors();
        const rows = Array.isArray(response)
          ? response
          : response?.vendors || response?.data || [];
        setVendors(rows);
      } catch (err) {
        console.error("Vendor directory loading failed:", err);
        setError("Unable to load vendor records.");
      } finally {
        setLoading(false);
      }
    }

    loadVendors();
  }, []);

  const normalizedVendors = useMemo(
    () =>
      vendors.map((vendor) => {
        const riskScore = Number(
          vendor.risk_score ?? vendor.riskScore ?? vendor.score ?? 0
        );
        const riskLevel = normalizeRisk(
          vendor.risk_level ?? vendor.riskLevel,
          riskScore
        );

        return {
          ...vendor,
          id: getVendorId(vendor),
          name: getVendorName(vendor),
          riskScore,
          riskLevel,
          paymentExposure: Number(
            vendor.payment_exposure ??
              vendor.paymentExposure ??
              vendor.exposure ??
              0
          ),
          lastChange:
            vendor.last_change ??
            vendor.lastChange ??
            vendor.changed_at ??
            "No recent change",
          gstin: vendor.gstin || "—",
          bankAccount: vendor.bank_account || vendor.bankAccount || "—",
          bankName: vendor.bank_name || vendor.bankName || "—",
        };
      }),
    [vendors]
  );

  const filteredVendors = useMemo(() => {
    const query = search.trim().toLowerCase();

    const result = normalizedVendors.filter((vendor) => {
      const matchesSearch =
        !query ||
        vendor.name.toLowerCase().includes(query) ||
        String(vendor.id || "").toLowerCase().includes(query) ||
        vendor.gstin.toLowerCase().includes(query) ||
        vendor.bankAccount.toLowerCase().includes(query);

      const matchesRisk =
        riskFilter === "ALL" || vendor.riskLevel === riskFilter;

      return matchesSearch && matchesRisk;
    });

    return [...result].sort((a, b) => {
      if (sortBy === "risk") return b.riskScore - a.riskScore;
      if (sortBy === "exposure") return b.paymentExposure - a.paymentExposure;
      return a.name.localeCompare(b.name);
    });
  }, [normalizedVendors, search, riskFilter, sortBy]);

  const stats = useMemo(() => {
    return normalizedVendors.reduce(
      (acc, vendor) => {
        acc.total += 1;
        acc[vendor.riskLevel.toLowerCase()] += 1;
        return acc;
      },
      { total: 0, low: 0, medium: 0, high: 0, critical: 0 }
    );
  }, [normalizedVendors]);

  const openVendorDNA = (id) => {
    if (id) window.location.href = `/vendor-dna/${id}`;
  };

  const openInvestigation = (id) => {
    if (id) window.location.href = `/investigation/${id}`;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-blue-600">
            Vendor intelligence
          </p>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
            Vendor Directory
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-500">
            Search vendor identities, review risk signals and open a deeper investigation before payment.
          </p>
        </div>

        <div className="inline-flex items-center gap-2 rounded-xl border border-blue-100 bg-blue-50 px-3 py-2 text-xs font-semibold text-blue-700">
          <Building2 size={14} />
          {formatNumber(stats.total)} vendors monitored
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <StatCard label="Low Risk" value={stats.low} icon={ShieldAlert} iconClass="bg-emerald-50 text-emerald-600" />
        <StatCard label="Medium Risk" value={stats.medium} icon={SlidersHorizontal} iconClass="bg-amber-50 text-amber-600" />
        <StatCard label="High Risk" value={stats.high} icon={TrendingUp} iconClass="bg-orange-50 text-orange-600" />
        <StatCard label="Critical" value={stats.critical} icon={ShieldAlert} iconClass="bg-red-50 text-red-600" />
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-col gap-3 border-b border-slate-100 p-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="relative min-w-0 flex-1 lg:max-w-xl">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search vendor, ID, GSTIN or bank account..."
              className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-9 pr-9 text-xs text-slate-800 outline-none transition focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-100"
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700"
              >
                <X size={14} />
              </button>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2">
              <Filter size={14} className="text-slate-400" />
              <select
                value={riskFilter}
                onChange={(event) => setRiskFilter(event.target.value)}
                className="bg-transparent text-xs font-semibold text-slate-700 outline-none"
              >
                <option value="ALL">All risk levels</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
              <ChevronDown size={13} className="text-slate-400" />
            </div>

            <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2">
              <SlidersHorizontal size={14} className="text-slate-400" />
              <select
                value={sortBy}
                onChange={(event) => setSortBy(event.target.value)}
                className="bg-transparent text-xs font-semibold text-slate-700 outline-none"
              >
                <option value="risk">Highest risk</option>
                <option value="exposure">Highest exposure</option>
                <option value="name">Name A–Z</option>
              </select>
              <ChevronDown size={13} className="text-slate-400" />
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex min-h-[360px] items-center justify-center">
            <div className="text-center">
              <div className="mx-auto h-9 w-9 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
              <p className="mt-3 text-sm font-semibold text-slate-700">Loading vendors...</p>
            </div>
          </div>
        ) : error ? (
          <div className="m-6 rounded-xl border border-red-200 bg-red-50 p-5 text-center">
            <p className="text-sm font-semibold text-red-700">{error}</p>
            <p className="mt-1 text-xs text-red-500">Check the API connection and refresh the page.</p>
          </div>
        ) : filteredVendors.length === 0 ? (
          <div className="flex min-h-[300px] flex-col items-center justify-center px-6 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-400">
              <Search size={20} />
            </div>
            <p className="mt-3 text-sm font-semibold text-slate-700">No vendors found</p>
            <p className="mt-1 text-xs text-slate-400">Try a different search or risk filter.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[980px]">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/70">
                  <th className="px-6 py-3 text-left text-[10px] font-bold uppercase tracking-wider text-slate-400">Vendor</th>
                  <th className="px-4 py-3 text-left text-[10px] font-bold uppercase tracking-wider text-slate-400">Risk</th>
                  <th className="px-4 py-3 text-left text-[10px] font-bold uppercase tracking-wider text-slate-400">Exposure</th>
                  <th className="px-4 py-3 text-left text-[10px] font-bold uppercase tracking-wider text-slate-400">GSTIN</th>
                  <th className="px-4 py-3 text-left text-[10px] font-bold uppercase tracking-wider text-slate-400">Bank</th>
                  <th className="px-6 py-3 text-right text-[10px] font-bold uppercase tracking-wider text-slate-400">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredVendors.map((vendor) => (
                  <tr key={vendor.id} className="border-b border-slate-100 last:border-0 hover:bg-slate-50/70">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-xs font-bold text-slate-600">
                          {vendor.name
                            .split(" ")
                            .slice(0, 2)
                            .map((word) => word[0])
                            .join("")}
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-slate-900">{vendor.name}</p>
                          <p className="mt-0.5 text-[10px] text-slate-400">{vendor.id}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-slate-900">{vendor.riskScore}</span>
                        <RiskBadge level={vendor.riskLevel} />
                      </div>
                    </td>
                    <td className="px-4 py-4 text-xs font-semibold text-slate-700">
                      {formatCurrency(vendor.paymentExposure)}
                    </td>
                    <td className="px-4 py-4 text-xs text-slate-500">{vendor.gstin}</td>
                    <td className="px-4 py-4">
                      <div>
                        <p className="text-xs font-semibold text-slate-700">{vendor.bankName}</p>
                        <p className="mt-0.5 text-[10px] text-slate-400">{vendor.bankAccount}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          onClick={() => openVendorDNA(vendor.id)}
                          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-[11px] font-semibold text-slate-700 hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
                        >
                          <Eye size={13} />
                          DNA
                        </button>
                        <button
                          type="button"
                          onClick={() => openInvestigation(vendor.id)}
                          className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-3 py-2 text-[11px] font-semibold text-white hover:bg-slate-800"
                        >
                          Investigate
                          <ArrowRight size={13} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="flex items-center justify-between border-t border-slate-100 px-6 py-3">
          <p className="text-[11px] text-slate-400">
            Showing <span className="font-semibold text-slate-600">{filteredVendors.length}</span> of {normalizedVendors.length} vendors
          </p>
          <p className="text-[10px] text-slate-400">Risk scores are explainable signals, not fraud verdicts.</p>
        </div>
      </section>
    </div>
  );
}
