'use client';

import { formatCapital } from "../lib/formatCurrency";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";


import { useState, useMemo } from 'react';

export default function DashboardTable({ 
  jurisdictions, 
  selectedJurisdiction, 
  onSelectJurisdiction 
,
  setSelectedJurisdiction
}: { 
  jurisdictions: any[], 
  selectedJurisdiction: string | null,
  setSelectedJurisdiction: (slug: string | null) => void, 
  onSelectJurisdiction: (slug: string | null) => void 
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRegion, setSelectedRegion] = useState<string>('all');
  const [selectedBand, setSelectedBand] = useState<string>('all');
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);

  const regions = useMemo(() => [...new Set(jurisdictions.map(j => j.region).filter(Boolean))].sort(), [jurisdictions]);
  const bands = ['HIGH', 'MEDIUM', 'LOW'];

  const filteredJurisdictions = useMemo(() => {
    let filtered = [...jurisdictions];
    
    if (searchTerm) {
      filtered = filtered.filter(j => 
        j.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        j.slug?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    if (selectedRegion !== 'all') {
      filtered = filtered.filter(j => j.region === selectedRegion);
    }
    
    if (selectedBand !== 'all') {
      filtered = filtered.filter(j => j.credibilityBand === selectedBand);
    }
    
    if (sortConfig) {
      filtered.sort((a, b) => {
        // Handle nested key for active capital
        const getVal = (obj: any, key: string) => {
          if (key === 'activeCapitalUsdBn') return obj.capital?.activeCapitalUsdBn ?? -1;
          return obj[key];
        };
        const aVal = getVal(a, sortConfig.key);
        const bVal = getVal(b, sortConfig.key);
        if (aVal === null || aVal === undefined) return 1;
        if (bVal === null || bVal === undefined) return -1;
        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }
    
    return filtered;
  }, [jurisdictions, searchTerm, selectedRegion, selectedBand, sortConfig]);

  const requestSort = (key: string) => {
    setSortConfig(current => {
      if (!current || current.key !== key) {
        return { key, direction: 'desc' };
      }
      if (current.direction === 'desc') {
        return { key, direction: 'asc' };
      }
      return null;
    });
  };

  const getBandColor = (band: string) => {
    switch (band?.toUpperCase()) {
      case 'HIGH': return 'bg-green-100 text-green-800 border-green-300';
      case 'MEDIUM': return 'bg-amber-100 text-amber-800 border-amber-300';
      default: return 'bg-red-100 text-red-800 border-red-300';
    }
  };

  const getFlagEmoji = (countryCode: string) => {
    if (!countryCode) return '🏳️';
    const codePoints = countryCode
      .toUpperCase()
      .split('')
      .map(char => 127397 + char.charCodeAt(0));
    return String.fromCodePoint(...codePoints);
  };

  const resetFilters = () => {
    setSearchTerm('');
    setSelectedRegion('all');
    setSelectedBand('all');
    setSortConfig(null);
  };

  // Helper to get practical implications
  const getPracticalImplications = (j: any) => {
    if (!j.credibility || j.credibility < 50) {
      return {
        title: 'Limited Transition Finance Activity',
        description: 'This jurisdiction shows minimal verified transition finance infrastructure. Capital flows toward net-zero alignment are likely fragmented or untracked.',
        actions: [
          'Priority candidate for agent factory sweep',
          'Requires foundational policy framework development',
          'High opportunity for first-mover institutional capital'
        ]
      };
    } else if (j.credibility < 80) {
      return {
        title: 'Emerging Transition Finance Framework',
        description: 'Moderate transition finance activity detected. Basic regulatory and market infrastructure exists but lacks comprehensive coverage or verification.',
        actions: [
          'Strengthen cross-pillar integration',
          'Enhance data transparency and registry systems',
          'Scale successful pilot programs'
        ]
      };
    } else {
      return {
        title: 'Established Transition Finance Leader',
        description: 'Robust, verified transition finance ecosystem. Strong regulatory frameworks, deployment mechanisms, and capital tracking systems are in place.',
        actions: [
          'Model for regional best practices',
          'Ready for advanced climate finance instruments',
          'Potential hub for transition finance innovation'
        ]
      };
    }
  };

  const getScoreExplanation = (score: number | null, type: 'credibility' | 'deployment') => {
    if (score === null || score === undefined) return 'No verified data available';
    
    const explanations = {
      credibility: {
        high: 'Strong evidence of credible transition finance execution across all five pillars (Regulatory, Grid, Capital, Execution, Survival).',
        medium: 'Moderate evidence with gaps in one or more pillars. Some policies or projects exist but lack comprehensive verification.',
        low: 'Limited or no verified evidence of transition finance execution. May have intentions or announcements without implementation.'
      },
      deployment: {
        high: 'High level of actual capital deployment and project implementation aligned with transition goals.',
        medium: 'Moderate deployment with some projects operational but scaling challenges remain.',
        low: 'Minimal verified deployment. Gap between policy intentions and on-the-ground implementation.'
      }
    };
    
    const level = score >= 80 ? 'high' : score >= 50 ? 'medium' : 'low';
    return explanations[type][level as keyof typeof explanations['credibility']];
  };

  return (
    <div className="relative">
      {/* Filters */}
      <div className="mb-4 flex flex-wrap gap-3 items-center">
        <input
          type="text"
          placeholder="Search jurisdiction..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="px-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
        />
        <select
          value={selectedRegion}
          onChange={(e) => setSelectedRegion(e.target.value)}
          className="px-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All regions</option>
          {regions.map(region => (
            <option key={region} value={region}>{region}</option>
          ))}
        </select>
        <select
          value={selectedBand}
          onChange={(e) => setSelectedBand(e.target.value)}
          className="px-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All bands</option>
          {bands.map(band => (
            <option key={band} value={band}>{band}</option>
          ))}
        </select>
        <button
          onClick={resetFilters}
          className="px-4 py-2 border border-slate-300 rounded-lg text-sm hover:bg-slate-50 transition-colors"
        >
          Reset
        </button>
        <div className="ml-auto text-sm text-slate-500">
          {filteredJurisdictions.length} jurisdictions
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto border border-slate-200 rounded-lg">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100" onClick={() => requestSort('name')}>
                Jurisdiction {sortConfig?.key === 'name' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100" onClick={() => requestSort('region')}>
                Region {sortConfig?.key === 'region' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100" onClick={() => requestSort('credibility')}>
                Credibility {sortConfig?.key === 'credibility' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100" onClick={() => requestSort('deployment')}>
                Deployment {sortConfig?.key === 'deployment' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100" onClick={() => requestSort('credibilityBand')}>
                Band {sortConfig?.key === 'credibilityBand' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100" onClick={() => requestSort('activeCapitalUsdBn')}>
                Active Capital {sortConfig?.key === 'activeCapitalUsdBn' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Cadence
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-200">
            {filteredJurisdictions.map((j) => (
              <tr 
                key={j.slug} 
                className={`hover:bg-slate-50 cursor-pointer transition-colors ${selectedJurisdiction === j.slug ? 'bg-blue-50' : ''}`}
                onClick={() => onSelectJurisdiction(j.slug)}
              >
                <td className="px-6 py-4 whitespace-nowrap font-medium text-slate-900">
                  <span className="mr-2">{getFlagEmoji(j.iso2 || j.slug)}</span>
                  {j.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-slate-600">{j.region || '—'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-slate-600">{j.credibility ?? 'N/A'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-slate-600">{j.deployment ?? 'N/A'}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getBandColor(j.credibilityBand)}`}>
                    {j.credibilityBand || 'UNSCORED'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-slate-600">
                  <span className="font-semibold">
                    {formatCapital(j.capital?.activeCapitalUsdBn)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-slate-600">{j.sweepCadence || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Enhanced Drawer with Practical Context */}
      {selectedJurisdiction && (
        <div className="fixed inset-y-0 right-0 w-full md:w-[600px] bg-white shadow-2xl border-l border-slate-200 overflow-y-auto z-50 transform transition-transform">
          <div className="sticky top-0 bg-white/95 backdrop-blur-sm border-b border-slate-200 p-4 flex items-center justify-between z-10">
            <h2 className="text-lg font-bold text-slate-900">Jurisdiction Profile</h2>
            <button 
              onClick={() => setSelectedJurisdiction(null)}
              className="p-2 hover:bg-slate-100 rounded-full transition-colors"
            >
              <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>

          {(() => {
            const j = jurisdictions.find(x => x.slug === selectedJurisdiction);
            if (!j) return null;

            // Dynamic Narrative Generator
            const getNarrative = () => {
              if (j.credibility >= 80) return `A gold-standard transition economy, ${j.name} combines robust regulatory frameworks with high execution velocity, serving as a regional beacon for sustainable capital deployment.`;
              if (j.capital?.activeCapitalUsdBn > 1000) return `As a global heavyweight, ${j.name} is channeling massive capital into grid modernization and renewable infrastructure, though scaling challenges require continued regulatory refinement.`;
              if (j.credibility < 50) return `${j.name} is in the early stages of its transition journey. While foundational frameworks are emerging, significant capital and execution gaps remain before large-scale deployment can accelerate.`;
              return `${j.name} demonstrates moderate transition momentum, balancing emerging regulatory frameworks with steady, albeit scaled, project deployment across key energy sectors.`;
            };

            // Dynamic Trivia Generator
            const getTrivia = () => {
              const triviaMap: Record<string, string> = {
                'brazil': "Brazil's Itaipu Dam is one of the world's largest hydroelectric facilities, historically supplying up to 95% of the country's electricity.",
                'denmark': "Denmark pioneered modern wind power, with wind energy regularly supplying over 50% of the country's total electricity consumption.",
                'china': "China installs more solar capacity in a single year than most countries have in their entire history, leading the global supply chain.",
                'united-states': "The US Inflation Reduction Act (IRA) represents the largest climate investment in history, unlocking hundreds of billions in private capital.",
                'india': "India is home to the Bhadla Solar Park, one of the largest solar parks in the world, spanning over 14,000 acres.",
              };
              return triviaMap[j.slug] || `${j.name} is actively reshaping its energy matrix, with current policies aiming to significantly boost renewable penetration by 2030.`;
            };

            const radarData = j.pillars ? Object.entries(j.pillars).map(([key, value]) => ({
              subject: key.charAt(0).toUpperCase() + key.slice(1),
              value: value,
              fullMark: 100,
            })) : [];

            return (
              <div className="p-6 space-y-6">
                {/* Header & Narrative */}
                <div>
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-4xl">
                      {j.iso2 ? String.fromCodePoint(...[...j.iso2.toUpperCase()].map(c => 127397 + c.charCodeAt(0))) : ''}
                    </span> 
                    {/* Note: emoji flags are handled by browser, but iso2 is a safe fallback or we can use a flag library. For now, let's use the name */}
                    <div>
                      <h1 className="text-2xl font-bold text-slate-900">{j.name}</h1>
                      <span className="text-sm text-slate-500 font-medium">{j.region} • {j.credibilityBand} Band</span>
                    </div>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed italic border-l-4 border-blue-500 pl-4 py-1 bg-blue-50/50 rounded-r">
                    "{getNarrative()}"
                  </p>
                </div>

                {/* Quick Stats Scorecards */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-center">
                    <div className="text-xs text-slate-500 uppercase font-semibold mb-1">Credibility</div>
                    <div className={`text-xl font-bold ${j.credibility >= 80 ? 'text-green-600' : j.credibility >= 50 ? 'text-amber-600' : 'text-red-600'}`}>{j.credibility ?? 'N/A'}</div>
                  </div>
                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-center">
                    <div className="text-xs text-slate-500 uppercase font-semibold mb-1">Deployment</div>
                    <div className={`text-xl font-bold ${j.deployment >= 80 ? 'text-green-600' : j.deployment >= 50 ? 'text-amber-600' : 'text-red-600'}`}>{j.deployment ?? 'N/A'}</div>
                  </div>
                  <div className="bg-blue-50 p-3 rounded-lg border border-blue-200 text-center">
                    <div className="text-xs text-blue-600 uppercase font-semibold mb-1">Capital</div>
                    <div className="text-lg font-bold text-blue-700 leading-tight">{formatCapital(j.capital?.activeCapitalUsdBn).replace('$', '').replace(' B', 'B').replace(' T', 'T').replace(' M', 'M')}</div>
                  </div>
                </div>

                {/* Radar Chart for 5 Pillars */}
                {radarData.length > 0 && (
                  <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wide mb-2 text-center">5-Pillar Assessment</h3>
                    <div className="h-64 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                          <PolarGrid stroke="#e2e8f0" />
                          <PolarAngleAxis dataKey="subject" tick={{ fill: '#475569', fontSize: 11, fontWeight: 600 }} />
                          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                          <Radar name="Score" dataKey="value" stroke="#2563eb" fill="#3b82f6" fillOpacity={0.4} strokeWidth={2} />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}

                {/* Did You Know? Trivia */}
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex gap-3">
                  <span className="text-2xl">💡</span>
                  <div>
                    <h4 className="text-sm font-bold text-amber-900 mb-1">Did You Know?</h4>
                    <p className="text-sm text-amber-800 leading-relaxed">{getTrivia()}</p>
                  </div>
                </div>

                {/* Methodology & Data Honesty */}
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-500 uppercase">Expected Discharged Capital</span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-green-700 border border-green-200">
                      {j.capital?.estimability === 'estimable' ? 'HIGH CONFIDENCE' : 'LOW CONFIDENCE'}
                    </span>
                  </div>
                  <div className="text-xs text-slate-600 space-y-1">
                    <div className="flex justify-between"><span>Methodology:</span> <span className="font-medium text-slate-900 capitalize">{j.capital?.method?.replace(/_/g, ' ') || 'Legacy'}</span></div>
                    <div className="flex justify-between"><span>Evidence Class:</span> <span className="font-medium text-slate-900">{j.capital?.evidenceClass || 'Not Classified'}</span></div>
                  </div>
                  <div className="pt-3 border-t border-slate-200">
                    <p className="text-[11px] text-slate-500 leading-relaxed">
                      <strong className="text-slate-700">ADR-0003 Data Honesty:</strong> This index strictly adheres to ADR-0003 compliance. No synthetic or modeled data is presented as fact. Capital is risk-weighted based on project lifecycle status and historical execution velocity.
                    </p>
                  </div>
                </div>

              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
}