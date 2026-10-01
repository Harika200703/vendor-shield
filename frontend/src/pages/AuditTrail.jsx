import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Clock3, FileText, Shield } from "lucide-react";
import { getAuditLogs } from "../services/api";

export default function AuditTrail() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const result = await getAuditLogs();
        setLogs(Array.isArray(result) ? result : result?.logs || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const filteredLogs = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return logs;

    return logs.filter((log) =>
      JSON.stringify(log).toLowerCase().includes(query)
    );
  }, [logs, search]);

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center text-sm text-slate-500">
        Loading audit trail...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-blue-600">
            Governance
          </p>
          <h1 className="mt-1 text-2xl font-bold text-slate-900">
            Audit Trail
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Trace vendor-risk decisions, payment actions and system events.
          </p>
        </div>

        <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600">
          <Shield size={14} className="text-blue-600" />
          {logs.length} events
        </div>
      </div>

      <input
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        placeholder="Search audit events..."
        className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-xs outline-none focus:border-blue-400"
      />

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="space-y-5">
          {filteredLogs.map((log, index) => {
            const actor =
              log.actor || log.user || log.performedBy || "System";
            const action =
              log.action || log.event || log.activity || "Audit event";
            const timestamp =
              log.timestamp || log.createdAt || log.created_at || log.date;
            const description =
              log.description || log.details || log.message || "";

            return (
              <div key={log.id || index} className="flex gap-4">
                <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-50 text-blue-600">
                  {action.toLowerCase().includes("approve") ? (
                    <CheckCircle2 size={16} />
                  ) : (
                    <FileText size={16} />
                  )}
                </div>

                <div className="min-w-0 flex-1 border-b border-slate-100 pb-5">
                  <div className="flex flex-col justify-between gap-1 sm:flex-row">
                    <p className="text-xs font-bold text-slate-900">{action}</p>
                    <span className="inline-flex items-center gap-1 text-[10px] text-slate-400">
                      <Clock3 size={12} />
                      {timestamp || "Time unavailable"}
                    </span>
                  </div>

                  <p className="mt-1 text-[11px] font-semibold text-slate-500">
                    {actor}
                  </p>

                  {description && (
                    <p className="mt-2 text-xs leading-5 text-slate-500">
                      {description}
                    </p>
                  )}
                </div>
              </div>
            );
          })}

          {!filteredLogs.length && (
            <div className="py-10 text-center text-sm text-slate-400">
              No audit events found.
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
