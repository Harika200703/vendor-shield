import { getDashboard } from "../services/api";
import { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  Building2,
  CheckCircle2,
  Clock3,
  CreditCard,
  Database,
  IndianRupee,
  RefreshCw,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";

import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
} from "recharts";

import UploadZone from "../components/UploadZone";
import UploadProgress from "../components/UploadProgress";
import DatasetSummary from "../components/DatasetSummary";

const RISK_COLORS = {
  Low: "#16A34A",
  Medium: "#D97706",
  High: "#EA580C",
  Critical: "#DC2626",
};



function formatCurrency(value) {
  if (value >= 10000000) {
    return `₹${(value / 10000000).toFixed(2)}Cr`;
  }

  if (value >= 100000) {
    return `₹${(value / 100000).toFixed(2)}L`;
  }

  return `₹${Number(value).toLocaleString("en-IN")}`;
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString("en-IN");
}

function getRiskColor(level) {
  return (
    RISK_COLORS[
      level?.charAt(0) +
        level?.slice(1).toLowerCase()
    ] || "#94A3B8"
  );
}

function RiskBadge({ level }) {
  const styles = {
    LOW: "bg-emerald-50 text-emerald-700 border-emerald-200",
    MEDIUM: "bg-amber-50 text-amber-700 border-amber-200",
    HIGH: "bg-orange-50 text-orange-700 border-orange-200",
    CRITICAL: "bg-red-50 text-red-700 border-red-200",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-bold tracking-wide ${
        styles[level] ||
        "border-slate-200 bg-slate-50 text-slate-600"
      }`}
    >
      <span
        className="h-1.5 w-1.5 rounded-full"
        style={{
          backgroundColor: getRiskColor(level),
        }}
      />

      {level}
    </span>
  );
}

function StatCard({
  title,
  value,
  description,
  icon: Icon,
  iconClass,
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-start justify-between">
        <div
          className={`flex h-10 w-10 items-center justify-center rounded-xl ${iconClass}`}
        >
          <Icon size={19} />
        </div>

        <ArrowRight
          size={15}
          className="text-slate-300"
        />
      </div>

      <p className="mt-4 text-xs font-medium text-slate-500">
        {title}
      </p>

      <p className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
        {value}
      </p>

      <p className="mt-1 text-[11px] text-slate-400">
        {description}
      </p>
    </div>
  );
}

function ChartTooltip({ active, payload }) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-lg">
      <p className="text-xs font-semibold text-slate-900">
        {payload[0].name}
      </p>

      <p className="mt-1 text-sm font-bold text-slate-700">
        {payload[0].value} vendors
      </p>
    </div>
  );
}

export default function Dashboard() {
  const [uploadedFiles, setUploadedFiles] =
    useState([]);

  const [datasetSummary, setDatasetSummary] =
    useState(null);

  const [analysisRunning, setAnalysisRunning] =
    useState(false);

  const [analysisProgress, setAnalysisProgress] =
    useState(0);

  const [analysisStage, setAnalysisStage] =
    useState("upload");

  const [analysisComplete, setAnalysisComplete] =
    useState(false);

  const [dashboardData, setDashboardData] =
    useState(null);

  const [dashboardLoading, setDashboardLoading] =
    useState(false);

  const [dashboardError, setDashboardError] =
    useState("");
  useEffect(() => {
  async function loadDashboard() {
    try {
      setDashboardLoading(true);
      setDashboardError("");

      const data = await getDashboard();

      setDashboardData(data);
    } catch (error) {
      console.error(
        "Dashboard loading failed:",
        error
      );

      setDashboardError(
        "Unable to load dashboard data."
      );
    } finally {
      setDashboardLoading(false);
    }
  }

  if (analysisComplete) {
    loadDashboard();
  }
}, [analysisComplete]);  

  /*
   * ---------------------------------------------------------
   * Read CSV files directly in the browser.
   * This is frontend-only functionality.
   * ---------------------------------------------------------
   */

  async function inspectCSV(file) {
    return new Promise((resolve) => {
      const reader = new FileReader();

      reader.onload = (event) => {
        const text = event.target.result || "";

        const lines = text
          .split(/\r?\n/)
          .filter(
            (line) => line.trim().length > 0
          );

        const headerLine = lines[0] || "";

        const headers = headerLine
          .split(",")
          .map((header) =>
            header
              .trim()
              .replace(/^"|"$/g, "")
              .toLowerCase()
          )
          .filter(Boolean);

        const records = Math.max(
          lines.length - 1,
          0
        );

        resolve({
          name: file.name,
          records,
          headers,
          size: file.size,
        });
      };

      reader.onerror = () => {
        resolve({
          name: file.name,
          records: 0,
          headers: [],
          size: file.size,
          error: true,
        });
      };

      reader.readAsText(file);
    });
  }

  /*
   * ---------------------------------------------------------
   * Whenever UploadZone changes, inspect the CSV files.
   * ---------------------------------------------------------
   */

  useEffect(() => {
    async function inspectFiles() {
      if (!uploadedFiles.length) {
        setDatasetSummary(null);
        return;
      }

      const inspected = await Promise.all(
        uploadedFiles.map((item) =>
          inspectCSV(item.file)
        )
      );

      const findRecords = (name) => {
        const file = inspected.find((item) =>
          item.name
            .toLowerCase()
            .includes(name)
        );

        return file?.records || 0;
      };

      setDatasetSummary({
        files: inspected,

        vendorCount:
          findRecords("vendors.csv"),

        transactionCount:
          findRecords("transactions.csv"),

        changeCount:
          findRecords("vendor_changes.csv"),

        employeeCount:
          findRecords("employees.csv"),
      });
    }

    inspectFiles();
  }, [uploadedFiles]);

  /*
   * ---------------------------------------------------------
   * Simulated analysis pipeline.
   *
   * Later the backend will replace this with:
   *
   * POST /api/upload
   * POST /api/analyse
   * ---------------------------------------------------------
   */

  function analyseDataset() {
    if (!uploadedFiles.length) {
      return;
    }

    setAnalysisRunning(true);
    setAnalysisComplete(false);
    setAnalysisProgress(0);
    setAnalysisStage("upload");

    const stages = [
      {
        progress: 15,
        stage: "upload",
      },
      {
        progress: 35,
        stage: "validate",
      },
      {
        progress: 55,
        stage: "resolve",
      },
      {
        progress: 78,
        stage: "risk",
      },
      {
        progress: 100,
        stage: "prepare",
      },
    ];

    let index = 0;

    const timer = setInterval(() => {
      if (index >= stages.length) {
        clearInterval(timer);

        setTimeout(() => {
          setAnalysisRunning(false);
          setAnalysisComplete(true);
        }, 600);

        return;
      }

      const current = stages[index];

      setAnalysisProgress(
        current.progress
      );

      setAnalysisStage(current.stage);

      index += 1;
    }, 700);
  }

  function resetAnalysis() {
    setUploadedFiles([]);
    setDatasetSummary(null);
    setAnalysisComplete(false);
    setAnalysisRunning(false);
    setAnalysisProgress(0);
    setAnalysisStage("upload");
  }

  /*
   * ---------------------------------------------------------
   * Upload / analysis state
   * ---------------------------------------------------------
   */

  if (analysisRunning) {
    return (
      <div className="mx-auto max-w-4xl space-y-6">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-blue-600">
            Vendor intelligence
          </p>

          <h2 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
            Analysing your data
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Building an evidence-based view of your vendor
            ecosystem.
          </p>
        </div>

        <UploadProgress
          progress={analysisProgress}
          currentStage={analysisStage}
        />
      </div>
    );
  }

  /*
   * ---------------------------------------------------------
   * Upload state
   * ---------------------------------------------------------
   */

  if (!analysisComplete) {
    return (
      <div className="mx-auto max-w-6xl space-y-6">
        {/* Hero */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-8 text-white shadow-xl sm:p-10">
          {/* Decorative glow */}
          <div className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-blue-500/20 blur-3xl" />

          <div className="pointer-events-none absolute -bottom-32 left-1/3 h-72 w-72 rounded-full bg-indigo-500/10 blur-3xl" />

          <div className="relative">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.14em] text-blue-300">
              <Database size={12} />
              Vendor intelligence platform
            </div>

            <h2 className="mt-5 max-w-2xl text-3xl font-bold tracking-tight sm:text-4xl">
              Know who you're paying
              <span className="text-blue-400">
                {" "}
                before you pay.
              </span>
            </h2>

            <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-300">
              Upload your vendor and payment datasets to
              uncover identity relationships, banking
              changes, unusual behaviour and explainable
              risk signals.
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <div className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-[10px] text-slate-300">
                Identity intelligence
              </div>

              <div className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-[10px] text-slate-300">
                Banking signals
              </div>

              <div className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-[10px] text-slate-300">
                Relationship graph
              </div>

              <div className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-[10px] text-slate-300">
                Explainable risk
              </div>
            </div>
          </div>
        </div>

        {/* Upload card */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6 flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50">
                  <Database
                    size={16}
                    className="text-blue-600"
                  />
                </div>

                <h3 className="text-sm font-bold text-slate-900">
                  Data Intake
                </h3>
              </div>

              <p className="mt-2 text-xs text-slate-500">
                Start by uploading the datasets used by your
                finance team.
              </p>
            </div>

            {uploadedFiles.length > 0 && (
              <button
                type="button"
                onClick={resetAnalysis}
                className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-slate-400 hover:text-red-500"
              >
                <RefreshCw size={13} />
                Reset
              </button>
            )}
          </div>

          <UploadZone
            files={uploadedFiles}
            onFilesChange={setUploadedFiles}
          />
        </div>

        {/* Summary */}
        {datasetSummary && (
          <DatasetSummary
            summary={datasetSummary}
            onAnalyse={analyseDataset}
          />
        )}

        {/* Empty hint */}
        {!uploadedFiles.length && (
          <div className="flex items-center justify-center gap-2 py-2 text-[11px] text-slate-400">
            <ShieldAlert size={14} />

            Your data stays in the current browser session
            during this frontend demo.
          </div>
        )}
      </div>
    );
  }

  /*
   * ---------------------------------------------------------
   * ANALYSIS COMPLETE → REAL DASHBOARD
   * ---------------------------------------------------------
   */

  if (dashboardLoading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
          <p className="mt-4 text-sm font-semibold text-slate-700">
            Loading risk intelligence...
          </p>
          <p className="mt-1 text-xs text-slate-400">
            Preparing your vendor risk dashboard
          </p>
        </div>
      </div>
    );
  }

  if (dashboardError) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="rounded-2xl border border-red-200 bg-red-50 px-6 py-5 text-center">
          <p className="text-sm font-semibold text-red-700">
            Unable to load dashboard
          </p>
          <p className="mt-1 text-xs text-red-500">
            {dashboardError}
          </p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <p className="text-sm text-slate-500">
          Preparing dashboard...
        </p>
      </div>
    );
  }

  const data = dashboardData;

  return (
    <div className="space-y-6">
      {/* Success banner */}
      <div className="flex flex-col justify-between gap-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-5 sm:flex-row sm:items-center">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100">
            <CheckCircle2
              size={20}
              className="text-emerald-600"
            />
          </div>

          <div>
            <p className="text-sm font-bold text-emerald-900">
              Analysis complete
            </p>

            <p className="mt-0.5 text-[11px] text-emerald-700">
              Vendor Shield identified risk signals across
              your uploaded datasets.
            </p>
          </div>
        </div>

        <button
          onClick={resetAnalysis}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-emerald-200 bg-white px-3 py-2 text-xs font-semibold text-emerald-700 hover:bg-emerald-50"
        >
          <Database size={14} />
          Upload new data
        </button>
      </div>

      {/* Heading */}
      <div>
        <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-blue-600">
          Risk overview
        </p>

        <h2 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
          Vendor Risk Command Center
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Monitor vendor risk, payment exposure and changes
          across your finance operations.
        </p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard
          title="Total Vendors"
          value={formatNumber(data.totalVendors)}
          description="Active vendor records"
          icon={Building2}
          iconClass="bg-blue-50 text-blue-600"
        />

        <StatCard
          title="High Risk Vendors"
          value={data.highRiskVendors}
          description="Require closer review"
          icon={TrendingUp}
          iconClass="bg-orange-50 text-orange-600"
        />

        <StatCard
          title="Critical Vendors"
          value={data.criticalVendors}
          description="Immediate investigation"
          icon={ShieldAlert}
          iconClass="bg-red-50 text-red-600"
        />

        <StatCard
          title="Changes Today"
          value={data.changesToday}
          description="Vendor profile changes"
          icon={Clock3}
          iconClass="bg-amber-50 text-amber-600"
        />

        <StatCard
          title="Pending Approvals"
          value={data.pendingApprovals}
          description="Payments awaiting action"
          icon={CreditCard}
          iconClass="bg-violet-50 text-violet-600"
        />
      </div>

      {/* Exposure */}
      <div className="flex flex-col justify-between gap-4 rounded-2xl border border-blue-100 bg-gradient-to-r from-blue-50 to-white p-5 sm:flex-row sm:items-center">
        <div className="flex items-center gap-4">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm">
            <IndianRupee size={20} />
          </div>

          <div>
            <p className="text-xs font-medium text-blue-700">
              Payment exposure under monitoring
            </p>

            <p className="mt-0.5 text-2xl font-bold text-slate-900">
              {formatCurrency(
                data.paymentExposure
              )}
            </p>
          </div>
        </div>

        <div className="rounded-lg bg-white px-3 py-2 text-xs font-medium text-slate-500 shadow-sm">
          Across current payment workflows
        </div>
      </div>

      {/* Chart + vendors */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-5">
        {/* Chart */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm xl:col-span-2">
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Risk Distribution
            </h3>

            <p className="mt-1 text-xs text-slate-400">
              Current vendor portfolio
            </p>
          </div>

          <div className="relative mt-5 h-[240px]">
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <PieChart>
                <Pie
                  data={data.riskDistribution}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={62}
                  outerRadius={90}
                  paddingAngle={3}
                  stroke="none"
                >
                  {data.riskDistribution.map(
                    (entry) => (
                      <Cell
                        key={entry.name}
                        fill={
                          RISK_COLORS[
                            entry.name
                          ]
                        }
                      />
                    )
                  )}
                </Pie>

                <Tooltip
                  content={<ChartTooltip />}
                />
              </PieChart>
            </ResponsiveContainer>

            <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <p className="text-3xl font-bold text-slate-900">
                  {data.totalVendors}
                </p>

                <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
                  Vendors
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {data.riskDistribution.map(
              (item) => (
                <div
                  key={item.name}
                  className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2"
                >
                  <div className="flex items-center gap-2">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{
                        backgroundColor:
                          RISK_COLORS[
                            item.name
                          ],
                      }}
                    />

                    <span className="text-xs text-slate-600">
                      {item.name}
                    </span>
                  </div>

                  <span className="text-xs font-bold text-slate-900">
                    {item.value}
                  </span>
                </div>
              )
            )}
          </div>
        </section>

        {/* Critical vendors */}
        <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm xl:col-span-3">
          <div className="flex items-start justify-between border-b border-slate-100 px-6 py-5">
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                Vendors Requiring Attention
              </h3>

              <p className="mt-1 text-xs text-slate-400">
                Highest current risk signals
              </p>
            </div>

            <button
              type="button"
              className="text-xs font-semibold text-blue-600 hover:text-blue-700"
            >
              View all
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px]">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/70">
                  <th className="px-6 py-3 text-left text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Vendor
                  </th>

                  <th className="px-4 py-3 text-left text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Risk
                  </th>

                  <th className="px-4 py-3 text-left text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Exposure
                  </th>

                  <th className="px-4 py-3 text-left text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Last Change
                  </th>

                  <th className="px-6 py-3 text-right text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Action
                  </th>
                </tr>
              </thead>

              <tbody>
                {data.criticalVendors.map(
                  (vendor) => (
                    <tr
                      key={vendor.id}
                      className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-xs font-bold text-slate-600">
                            {vendor.name
                              .split(" ")
                              .slice(0, 2)
                              .map(
                                (word) =>
                                  word[0]
                              )
                              .join("")}
                          </div>

                          <div>
                            <p className="text-xs font-semibold text-slate-900">
                              {vendor.name}
                            </p>

                            <p className="mt-0.5 text-[10px] text-slate-400">
                              {vendor.id}
                            </p>
                          </div>
                        </div>
                      </td>

                      <td className="px-4 py-4">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-slate-900">
                            {vendor.riskScore}
                          </span>

                          <RiskBadge
                            level={
                              vendor.riskLevel
                            }
                          />
                        </div>
                      </td>

                      <td className="px-4 py-4 text-xs font-semibold text-slate-700">
                        {formatCurrency(
                          vendor.paymentExposure
                        )}
                      </td>

                      <td className="px-4 py-4">
                        <div className="flex items-center gap-1.5 text-xs text-slate-500">
                          <Clock3 size={13} />
                          {vendor.lastChange}
                        </div>
                      </td>

                      <td className="px-6 py-4 text-right">
                        <button
                          type="button"
                          onClick={() => {
                            window.location.href =
                              `/investigation/${vendor.id}`;
                          }}
                          className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-3 py-2 text-[11px] font-semibold text-white hover:bg-slate-800"
                        >
                          Investigate
                          <ArrowRight
                            size={13}
                          />
                        </button>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      {/* Signal cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="flex items-start gap-3 rounded-xl border border-red-100 bg-red-50/50 p-4">
          <AlertTriangle
            size={17}
            className="mt-0.5 shrink-0 text-red-500"
          />

          <div>
            <p className="text-xs font-bold text-red-900">
              Critical signal detected
            </p>

            <p className="mt-1 text-[11px] leading-4 text-red-700">
              ABC Industrial has a recent bank change
              connected to a high-value payment.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3 rounded-xl border border-amber-100 bg-amber-50/50 p-4">
          <Clock3
            size={17}
            className="mt-0.5 shrink-0 text-amber-600"
          />

          <div>
            <p className="text-xs font-bold text-amber-900">
              {data.changesToday} changes today
            </p>

            <p className="mt-1 text-[11px] leading-4 text-amber-700">
              Banking, identity and profile changes require
              continuous review.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3 rounded-xl border border-blue-100 bg-blue-50/50 p-4">
          <CreditCard
            size={17}
            className="mt-0.5 shrink-0 text-blue-600"
          />

          <div>
            <p className="text-xs font-bold text-blue-900">
              Approval queue active
            </p>

            <p className="mt-1 text-[11px] leading-4 text-blue-700">
              {data.pendingApprovals} payments are waiting
              for finance action.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}