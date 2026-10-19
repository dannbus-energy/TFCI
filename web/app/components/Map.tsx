import { useMemo } from 'react';
'use client';

import { useEffect, useState } from 'react';
import { formatCapital } from "../lib/formatCurrency";
import Map, { Source, Layer, Popup } from 'react-map-gl/maplibre';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

if (typeof window !== 'undefined') {
  try {
    // @ts-ignore
    maplibregl.setWorkerUrl('/maplibre-gl-worker.mjs');
  } catch (e) {
    console.warn('Could not set worker URL', e);
  }
}

export default function MapComponent({ jurisdictions, onSelectJurisdiction }: { 
  jurisdictions: any[], 
  onSelectJurisdiction: (slug: string) => void 
}) {
  const [geoJsonData, setGeoJsonData] = useState<any>(null);
  const [hoverInfo, setHoverInfo] = useState<any>(null);

  // Deduplicate GeoJSON for labels (keep only the first polygon per country to prevent repeating names)
  const labelGeoJson = useMemo(() => {
    if (!geoJsonData) return null;
    const seen = new Set();
    const features = geoJsonData.features.filter(f => {
      const id = f.properties.matchedSlug || f.properties.name;
      if (seen.has(id)) return false;
      seen.add(id);
      return true;
    });
    return { type: 'FeatureCollection', features };
  }, [geoJsonData]);

  useEffect(() => {
    const jDict = jurisdictions.reduce((acc, j) => {
      const slug = j.slug?.toLowerCase() || '';
      if (slug) acc[slug] = j;
      if (j.name) acc[j.name.toLowerCase()] = j;
      return acc;
    }, {} as Record<string, any>);

    fetch('/map/tfci_jurisdiction_boundaries_simplified.geojson')
      .then(res => res.json())
      .then(data => {
        const validFeatures = data.features.map((f: any) => {
          const props = f.properties || {};
          const rawIdentifier = (props.tfciSlug || props.slug || props.iso2 || props.name || '').toLowerCase();
          
          const jData = jDict[rawIdentifier];
          const isTracked = !!jData;
          
          const finalData = jData || { 
            credibility: null, 
            credibilityBand: 'UNTRACKED', 
            activeCapitalUsdBn: null, 
            name: props.name || 'Out of Scope' 
          };
          
          const matchedSlug = finalData.slug || rawIdentifier;
          
          return {
            type: 'Feature',
            geometry: f.geometry,
            properties: { 
              matchedSlug: matchedSlug,
              credibility: finalData.credibility, 
              band: finalData.credibilityBand,
              capital: finalData?.capital?.activeCapitalUsdBn ?? null,
              name: finalData.name,
              isTracked: isTracked,
              // Ensure isPrimary is explicitly a boolean
              isPrimary: props.isPrimary === true
            }
          };
        });

        setGeoJsonData({ type: 'FeatureCollection', features: validFeatures });
      })
      .catch(err => console.error('❌ Failed to load GeoJSON:', err));
  }, [jurisdictions]);

  if (!geoJsonData) {
    return <div className="w-full h-[600px] bg-slate-100 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500">Loading map data...</div>;
  }

  return (
    <div className="relative w-full h-[600px] rounded-lg border border-slate-200 overflow-hidden bg-slate-50">
      <Map
        initialViewState={{ longitude: 10, latitude: 20, zoom: 1.5 }}
        style={{ width: '100%', height: '100%' }}
        mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
        interactiveLayerIds={['jurisdictions-fill']}
        onMouseMove={(e) => {
          if (e.features && e.features.length > 0) {
            const feature = e.features[0];
            setHoverInfo({
              longitude: e.lngLat.lng,
              latitude: e.lngLat.lat,
              feature: feature.properties
            });
          } else {
            setHoverInfo(null);
          }
        }}
        onMouseLeave={() => setHoverInfo(null)}
        onClick={(e) => {
          if (e.features && e.features.length > 0) {
            const feature = e.features[0];
            if (feature.properties.matchedSlug && onSelectJurisdiction) {
              onSelectJurisdiction(feature.properties.matchedSlug);
            }
          }
        }}
      >
        {geoJsonData && (
          <Source id="jurisdictions" type="geojson" data={geoJsonData}>
            <Layer
              id="jurisdictions-fill"
              type="fill"
              source="jurisdictions"
              paint={{
                'fill-color': [
                  'match',
                  ['get', 'band'],
                  'HIGH', '#10b981',
                  'MEDIUM', '#f59e0b',
                  'LOW', '#ef4444',
                  '#cbd5e1'
                ],
                'fill-opacity': 0.6
              }}
            />
            <Layer
              id="jurisdictions-border"
              type="line"
              source="jurisdictions"
              paint={{
                'line-color': '#ffffff',
                'line-width': 1
              }}
            />
          </Source>
        )}

        {labelGeoJson && (
          <Source id="jurisdictions-labels-source" type="geojson" data={labelGeoJson}>
            <Layer
              id="jurisdictions-labels"
              type="symbol"
              layout={{
                'text-field': ['get', 'name'],
                'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
                'text-offset': [0, 0.6],
                'text-anchor': 'center',
                'text-size': 11,
                'text-max-width': 8,
                'text-allow-overlap': false,
                'text-ignore-placement': false,
                'text-padding': 40
              }}
              paint={{
                'text-color': '#1e293b',
                'text-halo-color': '#ffffff',
                'text-halo-width': 1.5
              }}
            />
          </Source>
        )}

        {hoverInfo && hoverInfo.feature && (
          <Popup
            longitude={hoverInfo.longitude}
            latitude={hoverInfo.latitude}
            anchor="bottom"
            offset={[0, -10]}
            closeButton={false}
            closeOnClick={false}
            className="custom-map-popup"
          >
            <div className="p-2 min-w-[150px]" style={{ pointerEvents: "none" }}>
              <div className="font-bold text-sm text-slate-900 mb-1">{hoverInfo.feature.name}</div>
              <div className="text-xs text-slate-600 mb-1">Band: <span className="font-semibold">{hoverInfo.feature.band}</span></div>
              <div className="text-xs text-slate-600">
                Capital: <span className="font-semibold text-blue-600">{formatCapital(hoverInfo.feature.capital)}</span>
              </div>
            </div>
          </Popup>
        )}
      </Map>
    </div>
  );
}
