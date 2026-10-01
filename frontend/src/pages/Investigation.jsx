import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  CheckCircle2,
  FileSearch,
  ShieldAlert,
} from "lucide-react";
import { getInvestigation } from "../services/api";

const levelClass = {
  LOW: "text-emerald-700 bg-emerald-50 border-emerald-200",
  MEDIUM: "text-amber-700 bg-amber-50 border-amber-200",
  HIGH: "text-orange-700 bg-orange-50 border-orange-200",
  CRITICAL: "text-red-700 bg-red-50 border-red-200",
};

export default function Investigation() {
  const { vendorId } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError("");
        const result = await getInvestigation(vendorId);
        setData(result);
      } catch (err) {
        console.error(err);
        setError("Unable to load investigation data.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [vendorId]);

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center text-sm text-slate-500">
        Loading investigation...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">
        {error || "Investigation data unavailable."}
      </div>
    );
  }

  const signals = data.signals || [];
  const timeline = data.timeline || [];
  const level = String(data.riskLevel || "HIGH").toUpperCase();

  return (
    <div className="space-y-6">
      <button
        type="button"
        onClick={() => navigate(`/vendors/${vendorId}`)}
        className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-900"
      >
        <ArrowLeft size={15} />
        Back to Vendor DNA
      </button>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col justify-between gap-5 md:flex-row md:items-center">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-blue-600">
              Investigation Workspace
            </p>
            <h1 className="mt-1 text-2xl font-bold text-slate-900">
              {data.vendorName || vendorId}
            </h1>
            <p className="mt-1 text-xs text-slate-400">
              Evidence-based vendor risk review
            </p>
          </div>

          <div className="text-left md:text-right">
            <span
              className={`inline-flex rounded-full border px-3 py-1 text-xs font-bold ${
                levelClass[level] || levelClass.HIGH
              }`}
            >
              {level}
            </span>
            <p className="mt-2 text-3xl font-bold text-slate-900">
              {data.riskScore ?? "—"}
            </p>
            <p className="text-[10px] uppercase tracking-wider text-slate-400">
              Risk score
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm xl:col-span-2">
          <div className="flex items-center gap-2">
            <ShieldAlert size={17} className="text-red-500" />
            <h2 className="text-sm font-bold text-slate-900">
              Detected Evidence
            </h2>
          </div>

          <div className="mt-4 space-y-3">
            {signals.map((signal, index) => (
              <div
                key={index}
                className="rounded-xl border border-slate-100 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs font-bold text-slate-900">
                    {signal.title || signal.type || `Signal ${index + 1}`}
                  </p>
                  {signal.severity && (
                    <span className="text-[10px] font-bold uppercase text-orange-600">
                      {signal.severity}
                    </span>
                  )}
                </div>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  {signal.description || signal.message || signal}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-2xl border border-blue-100 bg-blue-50/50 p-6">
          <div className="flex items-center gap-2">
            <FileSearch size={17} className="text-blue-600" />
            <h2 className="text-sm font-bold text-slate-900">
              AI Explanation
            </h2>
          </div>

          <p className="mt-4 text-xs leading-6 text-slate-600">
            {data.aiSummary ||
              data.summary ||
              "Risk signals are being evaluated from vendor identity, banking, transaction and change-history evidence."}
          </p>

          {data.exposure !== undefined && (
            <div className="mt-4 rounded-xl border border-blue-100 bg-white p-3">
              <p className="text-[10px] font-bold uppercase tracking-wider text-blue-600">
                Payment exposure
              </p>
              <p className="mt-1 text-lg font-bold text-slate-900">
                ₹{Number(data.exposure || 0).toLocaleString("en-IN")}
              </p>
            </div>
          )}

          {data.recommendedAction && (
            <div className="mt-4 rounded-xl border border-blue-100 bg-white p-3">
              <p className="text-[10px] font-bold uppercase tracking-wider text-blue-600">
                Recommended review action
              </p>
              <p className="mt-1 text-sm font-bold text-slate-900">
                {data.recommendedAction}
              </p>
            </div>
          )}
        </section>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-sm font-bold text-slate-900">
          Investigation Timeline
        </h2>

        <div className="mt-5 space-y-4">
          {timeline.map((item, index) => (
            <div key={index} className="flex gap-3">
              <div className="mt-0.5">
                <CheckCircle2 size={16} className="text-blue-600" />
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-900">
                  {item.title || item.event}
                </p>
                <p className="mt-1 text-[11px] text-slate-500">
                  {item.date || item.timestamp || ""}
                  {item.description || item.message
                    ? ` — ${item.description || item.message}`
                    : ""}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
