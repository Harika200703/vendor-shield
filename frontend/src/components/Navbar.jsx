import {
  Bell,
  Search,
  ChevronDown,
  ShieldCheck,
} from "lucide-react";

export default function Navbar() {
  return (
    <header className="fixed left-[250px] right-0 top-0 z-30 h-[76px] border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="flex h-full items-center justify-between px-8">
        {/* Left */}
        <div>
          <p className="text-xs font-medium text-slate-400">
            Finance Operations
          </p>

          <h1 className="text-[18px] font-semibold text-slate-900">
            Vendor Risk Command Center
          </h1>
        </div>

        {/* Right */}
        <div className="flex items-center gap-5">
          {/* Search */}
          <button
            type="button"
            className="hidden items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-400 transition hover:border-slate-300 hover:bg-white sm:flex"
          >
            <Search size={15} />

            <span>Search vendors...</span>

            <kbd className="ml-4 rounded border border-slate-200 bg-white px-1.5 py-0.5 text-[10px] text-slate-400">
              /
            </kbd>
          </button>

          {/* Notification */}
          <button
            type="button"
            className="relative flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition hover:bg-slate-100 hover:text-slate-800"
          >
            <Bell size={18} />

            <span className="absolute right-2 top-2 h-2 w-2 rounded-full border-2 border-white bg-red-500" />
          </button>

          {/* Environment */}
          <div className="hidden items-center gap-2 border-l border-slate-200 pl-5 md:flex">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50">
              <ShieldCheck
                size={16}
                className="text-emerald-600"
              />
            </div>

            <div>
              <p className="text-xs font-semibold text-slate-700">
                Secure Workspace
              </p>

              <p className="text-[10px] text-slate-400">
                Finance Admin
              </p>
            </div>

            <ChevronDown
              size={14}
              className="ml-1 text-slate-400"
            />
          </div>
        </div>
      </div>
    </header>
  );
}