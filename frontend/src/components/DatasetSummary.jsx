import {
  ArrowRight,
  CheckCircle2,
  Database,
  FileSpreadsheet,
  AlertTriangle,
  Rows3,
} from "lucide-react";

function formatNumber(value) {
  return Number(value || 0).toLocaleString("en-IN");
}

function ValidationPill({ valid }) {
  return (
    <span
      className={[
        "inline-flex items-center gap-1 rounded-full border px-2 py-1 text-[9px] font-bold",
        valid
          ? "border-emerald-200 bg-emerald-50 text-emerald-700"
          : "border-amber-200 bg-amber-50 text-amber-700",
      ].join(" ")}
    >
      {valid ? (
        <CheckCircle2 size={10} />
      ) : (
        <AlertTriangle size={10} />
      )}

      {valid ? "VALID" : "CHECK"}
    </span>
  );
}

export default function DatasetSummary({
  summary,
  onAnalyse,
  analysing = false,
}) {
  if (!summary) {
    return null;
  }

  const allValid = summary.allValid !== false;

  return (
    <div className="space-y-4">
      {/* Dataset overview */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50">
              <Database
                size={19}
                className="text-emerald-600"
              />
            </div>

            <div>
              <h3 className="text-sm font-bold text-slate-900">
                Dataset ready
              </h3>

              <p className="mt-0.5 text-[11px] text-slate-400">
                {allValid
                  ? "All uploaded datasets passed the initial validation."
                  : "Review the dataset warnings before starting analysis."}
              </p>
            </div>
          </div>

          <div
            className={[
              "flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[10px] font-bold",
              allValid
                ? "bg-emerald-50 text-emerald-700"
                : "bg-amber-50 text-amber-700",
            ].join(" ")}
          >
            {allValid ? (
              <CheckCircle2 size={12} />
            ) : (
              <AlertTriangle size={12} />
            )}

            {allValid ? "VALIDATED" : "REVIEW REQUIRED"}
          </div>
        </div>

        {/* Files */}
        <div className="mt-5 grid grid-cols-1 gap-3 md:grid-cols-2">
          {summary.files?.map((file) => {
            const validation = file.validation;
            const valid =
              !file.error &&
              (validation?.valid ?? true);

            return (
              <div
                key={file.name}
                className={[
                  "rounded-xl border p-3 transition",
                  valid
                    ? "border-slate-100 bg-slate-50/70"
                    : "border-amber-200 bg-amber-50/40",
                ].join(" ")}
              >
                <div className="flex items-start gap-3">
                  <div
                    className={[
                      "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg",
                      valid
                        ? "bg-blue-50"
                        : "bg-amber-100",
                    ].join(" ")}
                  >
                    <FileSpreadsheet
                      size={17}
                      className={
                        valid
                          ? "text-blue-600"
                          : "text-amber-600"
                      }
                    />
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="truncate text-xs font-semibold text-slate-800">
                          {file.name}
                        </p>

                        <p className="mt-0.5 text-[10px] text-slate-400">
                          {validation?.label ||
                            "CSV Dataset"}
                        </p>
                      </div>

                      <ValidationPill valid={valid} />
                    </div>

                    <div className="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-[10px] text-slate-400">
                      <span>
                        {formatNumber(file.records)} records
                      </span>

                      <span>•</span>

                      <span>
                        {file.headers?.length || 0} columns
                      </span>
                    </div>

                    {/* Detected columns */}
                    {validation?.matched?.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {validation.matched
                          .slice(0, 6)
                          .map((field) => (
                            <span
                              key={field}
                              className="rounded bg-white px-1.5 py-1 text-[8px] font-medium text-slate-500 ring-1 ring-slate-100"
                            >
                              ✓ {field}
                            </span>
                          ))}

                        {validation.matched.length > 6 && (
                          <span className="rounded bg-white px-1.5 py-1 text-[8px] font-medium text-slate-400 ring-1 ring-slate-100">
                            +{validation.matched.length - 6} more
                          </span>
                        )}
                      </div>
                    )}

                    {/* Missing columns */}
                    {validation?.missing?.length > 0 && (
                      <div className="mt-2 rounded-lg border border-amber-200 bg-white/70 px-2.5 py-2">
                        <p className="text-[9px] font-bold text-amber-800">
                          Missing required fields
                        </p>

                        <p className="mt-0.5 text-[9px] leading-4 text-amber-700">
                          {validation.missing.join(", ")}
                        </p>
                      </div>
                    )}

                    {file.error && (
                      <p className="mt-2 text-[9px] font-medium text-red-600">
                        This CSV could not be read.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2 text-slate-400">
            <Rows3 size={15} />

            <span className="text-[10px] font-semibold uppercase tracking-wider">
              Vendors
            </span>
          </div>

          <p className="mt-2 text-xl font-bold text-slate-900">
            {formatNumber(summary.vendorCount)}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2 text-slate-400">
            <Rows3 size={15} />

            <span className="text-[10px] font-semibold uppercase tracking-wider">
              Transactions
            </span>
          </div>

          <p className="mt-2 text-xl font-bold text-slate-900">
            {formatNumber(summary.transactionCount)}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2 text-slate-400">
            <Rows3 size={15} />

            <span className="text-[10px] font-semibold uppercase tracking-wider">
              Changes
            </span>
          </div>

          <p className="mt-2 text-xl font-bold text-slate-900">
            {formatNumber(summary.changeCount)}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2 text-slate-400">
            <Rows3 size={15} />

            <span className="text-[10px] font-semibold uppercase tracking-wider">
              Employees
            </span>
          </div>

          <p className="mt-2 text-xl font-bold text-slate-900">
            {formatNumber(summary.employeeCount)}
          </p>
        </div>
      </div>

      {/* Analyse action */}
      <div
        className={[
          "flex flex-col items-center justify-between gap-4 rounded-2xl border p-5 sm:flex-row",
          allValid
            ? "border-blue-100 bg-blue-50/50"
            : "border-amber-200 bg-amber-50/50",
        ].join(" ")}
      >
        <div>
          <p className="text-sm font-bold text-slate-900">
            {allValid
              ? "Ready to analyse"
              : "Validation required"}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            {allValid
              ? "Run Vendor Shield's risk intelligence pipeline across the uploaded datasets."
              : "Resolve the highlighted dataset fields before running risk analysis."}
          </p>
        </div>

        <button
          type="button"
          disabled={analysing || !allValid}
          onClick={onAnalyse}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-xs font-bold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {analysing
            ? "Analysing..."
            : "Analyse Dataset"}

          {!analysing && allValid && (
            <ArrowRight size={14} />
          )}
        </button>
      </div>
    </div>
  );
}
