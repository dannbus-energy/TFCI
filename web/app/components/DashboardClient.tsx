'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import DashboardTable from './DashboardTable';

const Map = dynamic(() => import('./Map'), { ssr: false });

export default function DashboardClient({ jurisdictions }: { jurisdictions: any[] }) {
  const [selectedJurisdiction, setSelectedJurisdiction] = useState<string | null>(null);

  return (
    <div className="space-y-8">
      <Map 
        jurisdictions={jurisdictions} 
        selectedJurisdiction={selectedJurisdiction}
          setSelectedJurisdiction={setSelectedJurisdiction} 
        onSelectJurisdiction={setSelectedJurisdiction} 
      />
      // @ts-ignore
          <DashboardTable 
        jurisdictions={jurisdictions} 
        selectedJurisdiction={selectedJurisdiction}
          setSelectedJurisdiction={setSelectedJurisdiction} 
        onSelectJurisdiction={setSelectedJurisdiction} 
      />
    </div>
  );
}
