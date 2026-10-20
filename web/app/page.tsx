import payload from "../data/TFCI_frontend_payload_v2.json";
import DashboardClient from "./components/DashboardClient";

export default function Home() {
  // Type assertion to bypass strict TS checks during static build
  const data = payload as any;
  
  // Extract the jurisdictions array to pass to the client component
  const jurisdictions = data?.jurisdictions || [];

  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-8">
      <header className="mb-8 max-w-7xl mx-auto">
        <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-2">Transition Finance Credibility Index</h1>
        <p className="text-slate-600 text-lg mb-6">Scoring {jurisdictions.length} jurisdictions on transition-finance execution credibility.</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200">
            <p className="text-sm text-slate-500">Active Capital</p>
            <p className="text-2xl font-bold text-slate-900">${data.metadata?.active_capital_usd_bn.toLocaleString()}B</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200">
            <p className="text-sm text-slate-500">Verified Coverage</p>
            <p className="text-2xl font-bold text-slate-900">{data.metadata?.verified_coverage_ratio}%</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200">
            <p className="text-sm text-slate-500">Credibility Gap</p>
            <p className="text-2xl font-bold text-red-600">{data.metadata?.credibility_gap}%</p>
          </div>
        </div>
      </header>
      
      {/* CORRECTED: Passing the jurisdictions array, not the whole data object */}
      <DashboardClient jurisdictions={jurisdictions} />
    </main>
  );
}
