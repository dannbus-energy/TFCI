import { formatCapital } from "./lib/formatCurrency";
import DashboardTable from './components/DashboardTable';
import DashboardClient from './components/DashboardClient';

export const metadata = {
  title: "TFCI Dashboard",
};

async function getMetaData() {
  const res = await Promise.resolve({ ok: true, json: async () => ({ jurisdictions: [] }) });
  if (!res.ok) throw new Error("Failed to fetch meta");
  return res.json();
}

async function getJurisdictions() {
  // Fetch all 208 rows so the client component can sort/filter instantly
  const res = await Promise.resolve({ ok: true, json: async () => ({ jurisdictions: [] }) });
  if (!res.ok) throw new Error("Failed to fetch jurisdictions");
  return res.json();
}

export default async function Home() {
  const [meta, jurisdictions] = await Promise.all([
    getMetaData(),
    getJurisdictions(),
  ]);

  const execRatio = meta.sweep_coverage_ratio ?? null;
  const credGap = meta.verified_coverage_ratio != null ? (100 - meta.verified_coverage_ratio).toFixed(1) : null;
  const ratioLive = meta.execution_ratio_live ?? 0;
  const activeCapital = formatCapital(meta.active_capital_usd_bn);
  
  // Lifted state for Map/Table drawer synchronization
    return (
    <main className="min-h-screen bg-white text-slate-900 p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-1">Transition Finance Credibility Index</h1>
          <p className="text-slate-500">Execution, not intent — 213 jurisdictions × 20 sectors × 5 pillars.</p>
        </header>

        {/* KPI Cards */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="border border-slate-200 rounded-lg p-6">
            <p className="text-3xl font-bold text-slate-900">{meta.jurisdictions}</p>
            <p className="text-xs font-semibold text-slate-500 uppercase mt-2">Jurisdictions × 20 sectors × 5 pillars</p>
          </div>
          <div className="border border-slate-200 rounded-lg p-6">
            <p className="text-3xl font-bold text-slate-900">{execRatio === null ? "—" : `${execRatio}%`}</p>
            <p className="text-xs font-semibold text-slate-500 uppercase mt-2">Global execution ratio</p>
            <p className="text-xs text-slate-400 mt-1">{ratioLive > 0 ? `live in ${ratioLive}` : "jurisdictions swept"}</p>
          </div>
          <div className="border-2 border-green-600 rounded-lg p-6">
            <p className="text-3xl font-bold text-green-700">{credGap === null ? "—" : `${credGap}%`}</p>
            <p className="text-xs font-semibold text-slate-500 uppercase mt-2">Credibility gap</p>
            <p className="text-xs text-slate-400 mt-1">unverified capital</p>
          </div>
          <div className="border border-slate-200 rounded-lg p-6">
            <p className="text-3xl font-bold text-slate-900">{activeCapital}</p>
            <p className="text-xs font-semibold text-slate-500 uppercase mt-2">Active capital tracked</p>
          </div>
        </section>

        {/* Pass data to the interactive client component */}
        <DashboardClient jurisdictions={[]} />
      </div>
          </div>
    </main>
  );
}
