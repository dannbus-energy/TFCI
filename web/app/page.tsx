import DashboardClient from './components/DashboardClient';
import payload from '../data/TFCI_frontend_payload_v2.json';

export default function Home() {
  // Ensure we always pass a valid array to the client component
  const jurisdictions = Array.isArray(payload) 
    ? payload 
    : (payload?.jurisdictions || []);

  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-8">
      <DashboardClient jurisdictions={jurisdictions} />
    </main>
  );
}
