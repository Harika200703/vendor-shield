import {
  LayoutDashboard,
  Building2,
  ShieldAlert,
  ClipboardCheck,
  History,
  ChevronRight,
  Shield,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const navigation = [
  {
    label: "Dashboard",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    label: "Vendor Directory",
    path: "/vendors",
    icon: Building2,
  },
  {
    label: "Investigations",
    path: "/investigation/V-1001",
    icon: ShieldAlert,
  },
  {
    label: "Approval Queue",
    path: "/approvals",
    icon: ClipboardCheck,
  },
  {
    label: "Audit Trail",
    path: "/audit",
    icon: History,
  },
];

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-[250px] flex-col border-r border-slate-200 bg-white">
      {/* Logo */}
      <div className="flex h-[76px] items-center border-b border-slate-200 px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 shadow-sm">
            <Shield
              size={21}
              strokeWidth={2.2}
              className="text-white"
            />
          </div>

          <div>
            <div className="text-[17px] font-bold tracking-tight text-slate-900">
              Vendor Shield
            </div>

            <div className="text-[10px] font-medium uppercase tracking-[0.14em] text-slate-400">
              Payment Intelligence
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-6">
        <div className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400">
          Workspace
        </div>

        <div className="space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === "/"}
                className={({ isActive }) =>
                  [
                    "group flex items-center gap-3 rounded-xl px-3 py-3",
                    "text-sm font-medium transition-colors",
                    isActive
                      ? "bg-blue-50 text-blue-700"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900",
                  ].join(" ")
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon
                      size={18}
                      strokeWidth={isActive ? 2.2 : 1.8}
                    />

                    <span className="flex-1">
                      {item.label}
                    </span>

                    <ChevronRight
                      size={15}
                      className={[
                        "transition-opacity",
                        isActive
                          ? "opacity-100"
                          : "opacity-0 group-hover:opacity-60",
                      ].join(" ")}
                    />
                  </>
                )}
              </NavLink>
            );
          })}
        </div>
      </nav>

      {/* Bottom status */}
      <div className="border-t border-slate-200 p-4">
        <div className="rounded-xl bg-slate-50 p-3">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
            </span>

            <span className="text-xs font-semibold text-slate-700">
              Monitoring active
            </span>
          </div>

          <p className="mt-2 text-[11px] leading-4 text-slate-400">
            Vendor risk signals are being monitored across your payment
            workflow.
          </p>
        </div>
      </div>
    </aside>
  );
}