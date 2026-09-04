import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polygon, useMap } from 'react-leaflet';
import L from 'leaflet';
import type { IoTNode, CitizenIncident, RiskPolygon } from '../types/dashboard';
import { MoreHorizontal, MapPin, Layers, Plus, Minus, X, Eye, ShieldAlert } from 'lucide-react';

// Custom Glowing Emerald Leaflet Icon
const createCustomIcon = (color: string, isPulse: boolean = false) => {
  return L.divIcon({
    className: 'custom-leaflet-marker',
    html: `
      <div style="position: relative; display: flex; align-items: center; justify-content: center;">
        ${isPulse ? `<div style="position: absolute; width: 32px; height: 32px; border-radius: 50%; background-color: ${color}; opacity: 0.4; animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>` : ''}
        <div style="width: 24px; height: 24px; border-radius: 50%; background-color: ${color}; border: 2px solid #ffffff; box-shadow: 0 0 14px ${color}; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; color: white;">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
        </div>
      </div>
    `,
    iconSize: [26, 26],
    iconAnchor: [13, 13]
  });
};

// Map Controller for smooth flyTo coordinate changes
const MapController: React.FC<{ focusCoords: [number, number] | null }> = ({ focusCoords }) => {
  const map = useMap();
  useEffect(() => {
    if (focusCoords) {
      map.flyTo(focusCoords, 14, { duration: 1.5 });
    }
  }, [focusCoords, map]);
  return null;
};

interface MapViewProps {
  iotNodes: IoTNode[];
  citizenIncidents: CitizenIncident[];
  riskPolygons?: RiskPolygon[];
  focusCoords: [number, number] | null;
}

export const MapView: React.FC<MapViewProps> = ({
  iotNodes,
  citizenIncidents,
  riskPolygons = [],
  focusCoords
}) => {
  const defaultCenter: [number, number] = [23.7271, 92.7176]; // North Eastern India (NER) Aizawl Hill Slope Sector
  const [showRiskPolygons, setShowRiskPolygons] = useState<boolean>(true);
  const [hoveredPolygonId, setHoveredPolygonId] = useState<string | null>(null);

  // Dynamic Polygon Styling based on Severity & Hover State
  const getPolygonStyle = (poly: RiskPolygon, isHovered: boolean) => {
    let fillColor = '#eab308';
    let color = '#ca8a04';
    let weight = 1.5;
    let baseOpacity = 0.20;

    if (poly.severity === 'LEVEL 3') {
      fillColor = '#ef4444';
      color = '#dc2626';
      weight = 2;
      baseOpacity = 0.30;
    } else if (poly.severity === 'LEVEL 2') {
      fillColor = '#f97316';
      color = '#ea580c';
      weight = 2;
      baseOpacity = 0.25;
    }

    return {
      fillColor,
      color,
      weight: isHovered ? weight + 1 : weight,
      fillOpacity: isHovered ? 0.50 : baseOpacity, // 50% opacity on hover
      dashArray: isHovered ? '4, 4' : undefined
    };
  };

  return (
    <div className="glass-panel-emerald-glow rounded-3xl p-4 flex flex-col h-[390px] justify-between relative overflow-hidden">
      
      {/* GIS Map Card Header */}
      <div className="flex items-center justify-between mb-2 px-1">
        <h2 className="text-base font-bold text-slate-800 tracking-tight flex items-center gap-2">
          <span>GIS Map (North Eastern Region)</span>
          {riskPolygons.length > 0 && (
            <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full border border-emerald-300">
              {riskPolygons.length} Active Risk Polygons
            </span>
          )}
        </h2>
        <button className="text-slate-400 hover:text-slate-600 transition-colors p-1">
          <MoreHorizontal className="w-5 h-5" />
        </button>
      </div>

      {/* Map Viewport Container */}
      <div className="relative flex-1 w-full h-[320px] rounded-2xl overflow-hidden shadow-inner border border-slate-200/80">
        
        {/* Floating Top-Left Legend Widget */}
        <div className="absolute top-3 left-3 z-[1000] glass-panel-light p-2.5 rounded-2xl shadow-lg border border-white/80 max-w-[165px] text-xs">
          <div className="font-bold text-slate-800 mb-1.5 text-[11px]">Legend</div>
          <div className="space-y-1.5 font-medium">
            <div className="flex items-center gap-2 text-slate-700">
              <div className="w-3 h-3 rounded-full bg-[#10b981] flex items-center justify-center text-white shrink-0">
                <MapPin className="w-2 h-2" />
              </div>
              <span className="text-[10px]">Active IoT Stations</span>
            </div>
            <div className="flex items-center gap-2 text-slate-700">
              <div className="w-3 h-3 rounded bg-orange-500 shrink-0" />
              <span className="text-[10px]">Landslide zones</span>
            </div>
            <div className="flex items-center gap-2 text-slate-700">
              <div className="w-3 h-3 rounded bg-gradient-to-r from-amber-400 via-orange-500 to-rose-600 shrink-0" />
              <span className="text-[10px]">Geotech Risk Polygons</span>
            </div>
          </div>
        </div>

        {/* Floating Top-Right Layer Toggle Widget: [x] Show Geotech Risk Polygons */}
        <div className="absolute top-3 right-3 z-[1000] flex items-center gap-2">
          <label className="flex items-center gap-2 bg-white/95 backdrop-blur-md text-slate-800 text-[11px] font-bold px-3 py-1.5 rounded-full shadow-md border border-slate-200 cursor-pointer hover:bg-white transition-all select-none">
            <input 
              type="checkbox"
              checked={showRiskPolygons}
              onChange={(e) => setShowRiskPolygons(e.target.checked)}
              className="accent-[#10b981] w-3.5 h-3.5 rounded cursor-pointer"
            />
            <Eye className="w-3.5 h-3.5 text-emerald-600" />
            <span>Show Geotech Risk Polygons</span>
          </label>

          <div className="hidden sm:flex items-center gap-1.5 bg-[#10b981]/90 backdrop-blur-md text-white text-[11px] font-semibold px-2.5 py-1.5 rounded-full shadow-md">
            <MapPin className="w-3 h-3 fill-white text-[#10b981]" />
            <span>Active IoT Stations</span>
            <button className="hover:bg-emerald-700/50 p-0.5 rounded-full ml-0.5">
              <X className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* Leaflet Light Relief Map */}
        <MapContainer
          center={defaultCenter}
          zoom={12}
          scrollWheelZoom={true}
          zoomControl={false}
          style={{ width: '100%', height: '100%' }}
        >
          <MapController focusCoords={focusCoords} />

          <TileLayer
            attribution='&copy; <a href="https://www.esri.com/">Esri</a> &copy; OpenStreetMap contributors'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"
          />

          {/* Active Hazard Zone Heatmap Overlay Circles - North East Slopes */}
          <Circle
            center={[23.7380, 92.7090]}
            radius={2200}
            pathOptions={{
              color: '#ef4444',
              fillColor: '#dc2626',
              fillOpacity: 0.4,
              stroke: false
            }}
          />
          <Circle
            center={[23.7210, 92.7210]}
            radius={1500}
            pathOptions={{
              color: '#f97316',
              fillColor: '#ea580c',
              fillOpacity: 0.35,
              stroke: false
            }}
          />

          {/* Dynamic Geotech Officer Risk Polygons (Layer Toggleable) */}
          {showRiskPolygons && riskPolygons.map((poly) => {
            const isHovered = hoveredPolygonId === poly.id;
            const style = getPolygonStyle(poly, isHovered);

            return (
              <Polygon
                key={poly.id}
                positions={poly.coords}
                pathOptions={style}
                eventHandlers={{
                  mouseover: () => setHoveredPolygonId(poly.id),
                  mouseout: () => setHoveredPolygonId(null)
                }}
              >
                {/* Interactive Glassmorphic Metadata Popup */}
                <Popup className="glass-popup">
                  <div className="p-2.5 font-sans space-y-2 max-w-[240px] text-slate-900">
                    <div className="flex items-start justify-between gap-1 border-b border-slate-200 pb-1.5">
                      <h4 className="font-extrabold text-xs text-slate-900 leading-tight">
                        {poly.name}
                      </h4>
                    </div>

                    {/* Hazard Severity Badge */}
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-semibold text-slate-500">Hazard Severity:</span>
                      <span className={`px-2 py-0.5 rounded-md text-[10px] font-black text-white uppercase tracking-wider flex items-center gap-1 ${
                        poly.severity === 'LEVEL 3' 
                          ? 'bg-rose-600 shadow-sm shadow-rose-500/30' 
                          : poly.severity === 'LEVEL 2' 
                          ? 'bg-orange-500 shadow-sm shadow-orange-500/30' 
                          : 'bg-amber-500 shadow-sm shadow-amber-500/30'
                      }`}>
                        <ShieldAlert className="w-3 h-3" />
                        {poly.severity === 'LEVEL 3' ? 'Critical Red Alert' : poly.severity === 'LEVEL 2' ? 'High Risk / Evacuate' : 'Alert / Moderate'}
                      </span>
                    </div>

                    {/* Geotechnical Instability Score */}
                    <div className="space-y-1 bg-slate-50 p-2 rounded-lg border border-slate-200">
                      <div className="flex justify-between text-[11px] font-semibold text-slate-700">
                        <span>Geotechnical Instability:</span>
                        <strong className={poly.instabilityScore > 75 ? 'text-rose-600' : 'text-amber-600'}>
                          {poly.instabilityScore}%
                        </strong>
                      </div>
                      <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${poly.instabilityScore > 75 ? 'bg-rose-600' : poly.instabilityScore > 50 ? 'bg-orange-500' : 'bg-amber-500'}`}
                          style={{ width: `${poly.instabilityScore}%` }}
                        />
                      </div>
                    </div>

                    {/* Primary Trigger */}
                    <div className="text-[11px] text-slate-700 font-medium">
                      Primary Trigger: <strong className="text-slate-900">{poly.primaryTrigger}</strong>
                    </div>

                    {/* Last Updated & Author Metadata */}
                    <div className="text-[9px] font-mono text-slate-500 border-t border-slate-200 pt-1.5 flex justify-between items-center">
                      <span>{poly.authorInfo || 'Geotech Officer #104'}</span>
                      <span>{poly.lastUpdated || 'Live Sync'}</span>
                    </div>
                  </div>
                </Popup>
              </Polygon>
            );
          })}

          {/* Deployed Active IoT Station Markers */}
          {iotNodes.map((node) => (
            <Marker
              key={node.id}
              position={[node.lat, node.lng]}
              icon={createCustomIcon('#10b981', node.status === 'critical')}
            >
              <Popup>
                <div className="p-1 min-w-[180px]">
                  <div className="font-bold text-sm text-emerald-700">{node.name}</div>
                  <div className="text-xs text-slate-600 font-mono mt-1">
                    <div>Tilt: +{node.tiltChange}°</div>
                    <div>Moisture: {node.moisture}%</div>
                    <div>Status: {node.status?.toUpperCase()}</div>
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Citizen Geotag Pins */}
          {citizenIncidents.map((inc) => (
            <Marker
              key={inc.id}
              position={[inc.lat, inc.lng]}
              icon={createCustomIcon('#10b981', false)}
            />
          ))}
        </MapContainer>

        {/* Floating Bottom-Left Terrain Map Pill */}
        <div className="absolute bottom-3 left-3 z-[1000] glass-panel-light px-2.5 py-1 rounded-xl text-[11px] font-semibold text-slate-700 flex items-center gap-1.5 shadow-md">
          <Layers className="w-3.5 h-3.5 text-emerald-600" />
          <span>NER Relief map</span>
        </div>

        {/* Floating Bottom-Right Zoom Controls */}
        <div className="absolute bottom-3 right-3 z-[1000] flex flex-col rounded-xl glass-panel-light overflow-hidden shadow-md border border-white">
          <button className="p-1.5 text-slate-700 hover:bg-white/80 transition-colors border-b border-slate-200/60">
            <Plus className="w-3.5 h-3.5" />
          </button>
          <button className="p-1.5 text-slate-700 hover:bg-white/80 transition-colors">
            <Minus className="w-3.5 h-3.5" />
          </button>
        </div>

      </div>
    </div>
  );
};
