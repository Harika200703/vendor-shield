import { useEffect, useMemo, useState } from "react";
import { Check, Clock3, ShieldAlert, X } from "lucide-react";
import { getApprovals, takeApprovalAction } from "../services/api";

const statusClass = {
  PENDING: "bg-amber-50 text-amber-700 border-amber-200",
  HOLD: "bg-red-50 text-red-700 border-red-200",
  APPROVED: "bg-emerald-50 text-emerald-700 border-emerald-200",
  REJECTED: "bg-slate-100 text-slate-600 border-slate-200",
};

const money = (value = 0) => `₹${Number(value || 0).toLocaleString("en-IN")}`;

export default function ApprovalQueue() {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [workingId, setWorkingId] = useState(null);
  const [filter, setFilter] = useState("PENDING");

  useEffect(() => {
    async function load() {
      try {
        const result = await getApprovals();
        setApprovals(Array.isArray(result) ? result : result?.approvals || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const filtered = useMemo(
    () =>
      approvals.filter((item) => {
        const status = String(item.status || "PENDING").toUpperCase();
        return filter === "ALL" || status === filter;
      }),
    [approvals, filter]
  );

  async function handleAction(item, action) {
    const transactionId =
      item.transactionId || item.transaction_id || item.id;

    try {
      setWorkingId(transactionId);
      await takeApprovalAction(transactionId, action);

      setApprovals((current) =>
        current.map((row) =>
          (row.transactionId || row.transaction_id || row.id) === transactionId
            ? { ...row, status: action }
            : row
        )
      );
    } catch (error) {
      console.error(error);
    } finally {
      setWorkingId(null);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center text-sm text-slate-500">
        Loading approval queue...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-blue-600">
          Payment controls
        </p>
        <h1 className="mt-1 text-2xl font-bold text-slate-900">
          Approval Queue
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Review risk-aware payment decisions before release.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {["PENDING", "HOLD", "APPROVED", "REJECTED", "ALL"].map((value) => (
          <button
            key={value}
            type="button"
            onClick={() => setFilter(value)}
            className={`rounded-lg border px-3 py-2 text-xs font-semibold ${
              filter === value
                ? "border-slate-900 bg-slate-900 text-white"
                : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
            }`}
          >
            {value}
          </button>
        ))}
      </div>

      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[850px] text-left">
            <thead className="border-b border-slate-100 bg-slate-50">
              <tr className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                <th className="px-5 py-3">Vendor</th>
                <th className="px-4 py-3">Transaction</th>
                <th className="px-4 py-3">Amount</th>
                <th className="px-4 py-3">Risk</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-5 py-3 text-right">Action</th>
              </tr>
            </thead>

            <tbody>
              {filtered.map((item) => {
                const id =
                  item.transactionId || item.transaction_id || item.id;
                const status = String(item.status || "PENDING").toUpperCase();

                return (
                  <tr
                    key={id}
                    className="border-b border-slate-100 last:border-0"
                  >
                    <td className="px-5 py-4">
                      <p className="text-xs font-semibold text-slate-900">
                        {item.vendorName || item.vendor_name || item.vendor || "Unknown vendor"}
                      </p>
                      <p className="mt-1 text-[10px] text-slate-400">
                        {item.vendorId || item.vendor_id || ""}
                      </p>
                    </td>

                    <td className="px-4 py-4 text-xs text-slate-600">{id}</td>

                    <td className="px-4 py-4 text-xs font-bold text-slate-900">
                      {money(item.amount)}
                    </td>

                    <td className="px-4 py-4">
                      <span className="inline-flex items-center gap-1 text-xs font-bold text-red-600">
                        <ShieldAlert size={13} />
                        {item.riskScore ?? item.risk_score ?? "—"}
                      </span>
                    </td>

                    <td className="px-4 py-4">
                      <span
                        className={`rounded-full border px-2.5 py-1 text-[10px] font-bold ${
                          statusClass[status] || statusClass.PENDING
                        }`}
                      >
                        {status}
                      </span>
                    </td>

                    <td className="px-5 py-4 text-right">
                      {status === "PENDING" ? (
                        <div className="flex justify-end gap-2">
                          <button
                            type="button"
                            disabled={workingId === id}
                            onClick={() => handleAction(item, "APPROVED")}
                            className="inline-flex items-center gap-1 rounded-lg bg-emerald-600 px-3 py-2 text-[11px] font-semibold text-white disabled:opacity-50"
                          >
                            <Check size={13} />
                            Approve
                          </button>

                          <button
                            type="button"
                            disabled={workingId === id}
                            onClick={() => handleAction(item, "HOLD")}
                            className="inline-flex items-center gap-1 rounded-lg bg-red-600 px-3 py-2 text-[11px] font-semibold text-white disabled:opacity-50"
                          >
                            <X size={13} />
                            Hold
                          </button>
                        </div>
                      ) : (
                        <span className="text-[11px] text-slate-400">
                          Action completed
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}

              {!filtered.length && (
                <tr>
                  <td colSpan="6" className="px-5 py-12 text-center">
                    <Clock3 className="mx-auto text-slate-300" size={22} />
                    <p className="mt-2 text-sm font-semibold text-slate-500">
                      No matching approvals
                    </p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
