"""TFCI Scoring Engine (skeleton). Standard v0.2 computations."""
import pandas as pd, numpy as np, math

def rhu(x):
    return int(math.floor(float(x) + 0.5))

def band(score):
    return 'HIGH' if score >= 75 else ('MEDIUM' if score >= 50 else 'LOW')

PILLAR_COLS = ['p1_subscore','p2_subscore','p3_subscore','p4_subscore','p5_subscore']

HORIZONS = {'utility-scale-renewables':7,'nuclear-clean-firm':15,'energy-storage-flexibility':6,
 'grid-modernization':12,'hydrogen-powerfuels':10,'carbon-markets':5,'critical-minerals':15,
 'water-security':10,'food-systems-agriculture':7,'ai-compute':5,'semiconductors':7,
 'advanced-manufacturing':6,'cyber-physical-security':5,'space-economy':8,'net-zero-mobility':8,
 'aviation-maritime':10,'buildings-heat':8,'smart-cities':10,'labor-transition':5,
 'digital-public-infrastructure':6}

class TfciData:
    def __init__(self, path):
        self.jurisdictions = pd.read_csv(f'{path}/jurisdictions.csv', encoding='utf-8')
        self.sectors = pd.read_csv(f'{path}/sectors.csv', encoding='utf-8')
        self.sector_scores = pd.read_csv(f'{path}/sector_scores.csv', encoding='utf-8')
        self.ledger_coverage = pd.read_csv(f'{path}/ledger_coverage.csv', encoding='utf-8')
        self.projects = pd.read_csv(f'{path}/projects.csv', encoding='utf-8')
        self.ledger_events = pd.read_csv(f'{path}/ledger_events.csv', encoding='utf-8')
        self.evidence_sources = pd.read_csv(f'{path}/evidence_sources.csv', encoding='utf-8')
        self.fx_rates = pd.read_csv(f'{path}/fx_rates.csv', encoding='utf-8')

def compute_rollup(scores):
    out = {}
    for jslug, g in scores.groupby('jurisdiction_slug'):
        subs = [rhu(g[c].mean()) for c in PILLAR_COLS]
        out[jslug] = {'subscores': subs, 'overall': rhu(np.mean(subs)), 'band': band(rhu(np.mean(subs)))}
    return out

def compute_deployment(scores, sectors):
    pools = dict(zip(sectors.sector_slug, sectors.capital_pool_usd_bn))
    out = {}
    for jslug, g in scores.groupby('jurisdiction_slug'):
        w = sum(pools[s]*v for s, v in zip(g.sector_slug, g.overall_score)) / sum(pools[s] for s in g.sector_slug)
        out[jslug] = {'score': rhu(w), 'band': band(rhu(w))}
    return out

def compute_cell_ratios(events, projects, horizons, as_of_date):
    if events is None or events.empty:
        return pd.DataFrame(columns=['jurisdiction_slug','sector_slug','announced_usd_bn',
                                     'commissioned_usd_bn','cancelled_usd_bn','execution_ratio','survival_ratio'])
    ev = events.merge(projects[['project_id','jurisdiction_slug','sector_slug']], on='project_id', how='left')
    ev['event_date'] = pd.to_datetime(ev.event_date); as_of = pd.to_datetime(as_of_date)
    rows = []
    for (j, s), g in ev.groupby(['jurisdiction_slug','sector_slug']):
        h = pd.Timedelta(days=365.25 * horizons.get(s, 10))
        cell = {'ann': 0.0, 'com': 0.0, 'can': 0.0, 'n': 0}
        for pid, pg in g.groupby('project_id'):
            pg = pg.sort_values('event_date')
            capex = pg[pg.capital_type == 'capex']
            anchor = capex[capex.event_type.isin(['announcement','capex_revision','fid']) & capex.capital_usd_bn.notna()]
            if anchor.empty: continue
            if (as_of - anchor.iloc[-1].event_date) < h: continue
            cell['n'] += 1
            cell['ann'] += float(anchor.iloc[-1].capital_usd_bn)
            cell['com'] += float(capex[capex.event_type.isin(['commissioning','partial_commissioning'])].capital_usd_bn.fillna(0).sum())
            cell['can'] += float(capex[capex.event_type=='cancellation'].capital_usd_bn.fillna(0).sum())
        if cell['n'] == 0: continue
        rows.append({'jurisdiction_slug': j, 'sector_slug': s, 'announced_usd_bn': cell['ann'],
                     'commissioned_usd_bn': cell['com'], 'cancelled_usd_bn': cell['can'],
                     'execution_ratio': cell['com']/cell['ann'] if cell['ann'] else None,
                     'survival_ratio': 1 - cell['can']/cell['ann'] if cell['ann'] else None})
    return pd.DataFrame(rows)

def export_frontend_payload(data, as_of_date):
    rollup = compute_rollup(data.sector_scores); deploy = compute_deployment(data.sector_scores, data.sectors)
    cov = data.ledger_coverage.set_index(['jurisdiction_slug','sector_slug']).ledger_status
    cred_rank = {j: i+1 for i, (j, _) in enumerate(sorted(rollup.items(), key=lambda kv: -kv[1]['overall']))}
    dep_rank = {j: i+1 for i, (j, _) in enumerate(sorted(deploy.items(), key=lambda kv: -kv[1]['score']))}
    ratios = compute_cell_ratios(data.ledger_events, data.projects, HORIZONS, as_of_date)
    cc = {}
    for _, r in ratios.iterrows():
        cc.setdefault(r.jurisdiction_slug, {'ann': 0.0, 'com': 0.0, 'can': 0.0})
        cc[r.jurisdiction_slug]['ann'] += r.announced_usd_bn
        cc[r.jurisdiction_slug]['com'] += r.commissioned_usd_bn
        cc[r.jurisdiction_slug]['can'] += r.cancelled_usd_bn
    out = {'asOf': as_of_date, 'jurisdictions': []}
    for _, j in data.jurisdictions.iterrows():
        slug = j.jurisdiction_slug
        cell_status = cov.loc[slug].iloc[0] if slug in cov.index.get_level_values(0) else 'not_yet_swept'
        c = cc.get(slug)
        ex = (c['com']/c['ann']) if c and c['ann'] else None
        sv = (1 - c['can']/c['ann']) if c and c['ann'] else None
        out['jurisdictions'].append({'slug': slug, 'name': j['name'], 'iso2': j.iso2, 'region': j.region,
            'sweepCadence': j.sweep_cadence, 'recomputeTier': j.recompute_tier,
            'credibility': rollup[slug]['overall'], 'credibilityBand': rollup[slug]['band'], 'credibilityRank': cred_rank[slug],
            'deployment': deploy[slug]['score'], 'deploymentBand': deploy[slug]['band'], 'deploymentRank': dep_rank[slug],
            'executionRatio': round(ex,4) if ex is not None else None,
            'survivalRatio': round(sv,4) if sv is not None else None,
            'credibilityGap': round(1-ex,4) if ex is not None else None,
            'ledgerStatus': cell_status, 'p5Anchor': 'analyst'})
    return out
