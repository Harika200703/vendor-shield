import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Building2,
  CreditCard,
  Network,
  ShieldAlert,
  Landmark,
} from "lucide-react";
import {
  getVendor,
  getVendorDNA,
  getVendorRelationships,
} from "../services/api";

const riskClass = {
  LOW: "bg-emerald-50 text-emerald-700 border-emerald-200",
  MEDIUM: "bg-amber-50 text-amber-700 border-amber-200",
  HIGH: "bg-orange-50 text-orange-700 border-orange-200",
  CRITICAL: "bg-red-50 text-red-700 border-red-200",
};

const money = (value = 0) =>
  `₹${Number(value || 0).toLocaleString("en-IN")}`;

function pick(obj, ...keys) {
  for (const key of keys) {
    if (obj?.[key] !== undefined && obj?.[key] !== null && obj?.[key] !== "") {
      return obj[key];
    }
  }
  return null;
}

export default function VendorDNA() {
  const { vendorId } = useParams();
  const navigate = useNavigate();

  const [vendor, setVendor] = useState(null);
  const [dna, setDna] = useState(null);
  const [relationships, setRelationships] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError("");

        const [vendorData, dnaData, relationshipData] = await Promise.all([
          getVendor(vendorId),
          getVendorDNA(vendorId),
          getVendorRelationships(vendorId),
        ]);

        setVendor(vendorData);
        setDna(dnaData);
        setRelationships(relationshipData);
      } catch (err) {
        console.error(err);
        setError("Unable to load vendor intelligence.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [vendorId]);

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center text-sm text-slate-500">
        Loading vendor intelligence...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">
        {error}
      </div>
    );
  }

  if (!vendor) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
        Vendor not found.
      </div>
    );
  }

  const risk = pick(vendor, "riskLevel", "risk_level") ||
    pick(dna, "riskLevel", "risk_level") ||
    "LOW";

  const riskScore = pick(
    vendor,
    "riskScore",
    "risk_score",
    "score"
  ) ?? pick(dna, "riskScore", "risk_score");

  const name = pick(vendor, "name", "vendor_name") || vendorId;
  const id = pick(vendor, "id", "vendor_id") || vendorId;

  const exposure = pick(
    vendor,
    "paymentExposure",
    "payment_exposure",
    "exposure"
  );

  const bankName = pick(vendor, "bankName", "bank_name") ||
    pick(dna, "bankName", "bank_name") ||
    "Not available";

  const bankAccount = pick(vendor, "bankAccount", "bank_account") ||
    pick(dna, "bankAccount", "bank_account") ||
    "Not available";

  const gstin = pick(vendor, "gstin", "GSTIN") ||
    pick(dna, "gstin", "GSTIN") ||
    "Not available";

  const lastChange = pick(
    vendor,
    "lastChange",
    "last_change",
    "changed_at"
  ) || "No recent change";

  const signals = dna?.signals || [];

  return (
    <div className="space-y-6">
      <button
        type="button"
        onClick={() => navigate("/vendors")}
        className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-900"
      >
        <ArrowLeft size={15} />
        Back to vendors
      </button>

      <div className="flex flex-col justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:flex-row md:items-center">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
            <Building2 size={25} />
          </div>
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-blue-600">
              Vendor DNA
            </p>
            <h1 className="mt-1 text-2xl font-bold text-slate-900">{name}</h1>
            <p className="mt-1 text-xs text-slate-400">{id}</p>
          </div>
        </div>

        <div className="text-left md:text-right">
          <div
            className={`inline-flex rounded-full border px-3 py-1 text-xs font-bold ${
              riskClass[String(risk).toUpperCase()] || riskClass.LOW
            }`}
          >
            {risk}
          </div>
          <p className="mt-2 text-3xl font-bold text-slate-900">
            {riskScore ?? "—"}
          </p>
          <p className="text-[10px] uppercase tracking-wider text-slate-400">
            Risk score
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <InfoCard
          icon={CreditCard}
          title="Payment Exposure"
          value={money(exposure)}
        />
        <InfoCard icon={Landmark} title="Bank" value={bankName} />
        <InfoCard
          icon={ShieldAlert}
          title="Last Change"
          value={lastChange}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-sm font-bold text-slate-900">
            Identity & Banking Profile
          </h2>

          <div className="mt-5 space-y-3">
            <Row label="Vendor ID" value={id} />
            <Row label="GSTIN" value={gstin} />
            <Row label="Bank Account" value={bankAccount} />
            <Row label="Bank Name" value={bankName} />
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-sm font-bold text-slate-900">Risk Signals</h2>

          <div className="mt-4 space-y-3">
            {signals.length ? (
              signals.map((signal, index) => (
                <div
                  key={index}
                  className="rounded-xl border border-amber-100 bg-amber-50/60 p-3"
                >
                  <p className="text-xs font-semibold text-amber-900">
                    {signal.title || signal.type || "Risk signal"}
                  </p>
                  <p className="mt-1 text-[11px] leading-4 text-amber-700">
                    {signal.description || signal.message || signal}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400">
                No risk signals available.
              </p>
            )}
          </div>
        </section>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-2">
          <Network size={17} className="text-blue-600" />
          <h2 className="text-sm font-bold text-slate-900">
            Relationship Intelligence
          </h2>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {(relationships?.nodes || []).map((node) => (
            <div
              key={node.id}
              className="rounded-xl border border-slate-100 bg-slate-50 p-3"
            >
              <p className="text-[10px] font-bold uppercase text-slate-400">
                {node.type || "Entity"}
              </p>
              <p className="mt-1 text-xs font-semibold text-slate-800">
                {node.data?.label || node.label || node.data?.name || node.name}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function InfoCard({ icon: Icon, title, value }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <Icon size={17} className="text-blue-600" />
      <p className="mt-3 text-[10px] font-bold uppercase tracking-wider text-slate-400">
        {title}
      </p>
      <p className="mt-1 text-sm font-bold text-slate-900">{value}</p>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-lg bg-slate-50 px-3 py-2.5">
      <span className="text-xs text-slate-500">{label}</span>
      <span className="max-w-[60%] break-all text-right text-xs font-semibold text-slate-800">
        {value}
      </span>
    </div>
  );
}
