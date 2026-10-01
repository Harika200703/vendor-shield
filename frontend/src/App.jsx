
import ApprovalQueue from "./pages/ApprovalQueue";
import AuditTrail from "./pages/AuditTrail";
import { Routes, Route, Navigate } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Vendors from "./pages/Vendors";
import VendorDNA from "./pages/VendorDNA";
import Investigation from "./pages/Investigation";

import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";

function Placeholder({ title }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-blue-600">
        Vendor Shield
      </div>

      <h1 className="text-2xl font-bold text-slate-900">
        {title}
      </h1>

      <p className="mt-2 text-sm text-slate-500">
        This workspace is being built.
      </p>
    </div>
  );
}

function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar />

      <Navbar />

      <main className="ml-[250px] min-h-screen pt-[76px]">
        <div className="p-8">
          <Routes>
            {/* Dashboard */}
            <Route path="/" element={<Dashboard />} />

            {/* Vendor Directory */}
            <Route path="/vendors" element={<Vendors />} />

            {/* Vendor DNA */}
            <Route
              path="/vendors/:vendorId"
              element={<VendorDNA />}
            />

            {/* Investigation */}
            <Route
              path="/investigation/:vendorId"
              element={<Investigation />}
            />

            {/* Remaining pages */}
            <Route
              path="/approvals"
              element={<ApprovalQueue />}
            />

            <Route
              path="/audit"
              element={<AuditTrail />}
            />

            {/* Unknown route */}
            <Route
              path="*"
              element={<Navigate to="/" replace />}
            />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default function App() {
  return <AppLayout />;
}