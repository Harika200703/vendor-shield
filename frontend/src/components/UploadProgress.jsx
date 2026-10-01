import {
  CheckCircle2,
  Circle,
  Loader2,
  Sparkles,
} from "lucide-react";

const stages = [
  {
    id: "upload",
    label: "Uploading datasets",
  },
  {
    id: "validate",
    label: "Validating records",
  },
  {
    id: "resolve",
    label: "Resolving vendor identities",
  },
  {
    id: "risk",
    label: "Detecting risk signals",
  },
  {
    id: "prepare",
    label: "Preparing risk intelligence",
  },
];

export default function UploadProgress({
  progress = 0,
  currentStage = "upload",
}) {
  const currentIndex = stages.findIndex(
    (stage) => stage.id === currentStage
  );

  return (
    <div className="overflow-hidden rounded-2xl border border-blue-100 bg-white shadow-sm">
      {/* Header */}
      <div className="border-b border-slate-100 bg-gradient-to-r from-blue-50 to-white p-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm">
            <Sparkles size={18} />
          </div>

          <div>
            <p className="text-sm font-bold text-slate-900">
              Analysing your data
            </p>

            <p className="mt-0.5 text-[11px] text-slate-500">
              Vendor Shield is building your risk intelligence.
            </p>
          </div>
        </div>
      </div>

      {/* Progress */}
      <div className="p-5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-600">
            Analysis progress
          </span>

          <span className="text-sm font-bold text-blue-600">
            {progress}%
          </span>
        </div>

        <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-blue-600 transition-all duration-500"
            style={{
              width: `${progress}%`,
            }}
          />
        </div>

        {/* Stages */}
        <div className="mt-6 space-y-4">
          {stages.map((stage, index) => {
            const completed =
              index < currentIndex ||
              progress >= 100;

            const active =
              index === currentIndex &&
              progress < 100;

            return (
              <div
                key={stage.id}
                className="flex items-center gap-3"
              >
                {completed ? (
                  <CheckCircle2
                    size={17}
                    className="shrink-0 text-emerald-500"
                  />
                ) : active ? (
                  <Loader2
                    size={17}
                    className="shrink-0 animate-spin text-blue-600"
                  />
                ) : (
                  <Circle
                    size={17}
                    className="shrink-0 text-slate-300"
                  />
                )}

                <span
                  className={[
                    "text-xs",
                    completed
                      ? "font-medium text-slate-700"
                      : active
                        ? "font-semibold text-blue-700"
                        : "text-slate-400",
                  ].join(" ")}
                >
                  {stage.label}
                </span>

                {active && (
                  <span className="ml-auto text-[10px] font-medium text-blue-500">
                    Processing...
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}