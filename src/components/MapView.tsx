import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import type { IoTNode, CitizenIncident } from '../types/dashboard';
import { MoreHorizontal, MapPin, Layers, Plus, Minus, X } from 'lucide-react';

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
  focusCoords: [number, number] | null;
}

export const MapView: React.FC<MapViewProps> = ({
  iotNodes,
  citizenIncidents,
  focusCoords
}) => {
  const defaultCenter: [number, number] = [23.7271, 92.7176]; // North Eastern India (NER) Aizawl Hill Slope Sector

  return (
    <div className="glass-panel-emerald-glow rounded-3xl p-4 flex flex-col h-[390px] justify-between relative overflow-hidden">
      
      {/* GIS Map Card Header */}
      <div className="flex items-center justify-between mb-2 px-1">
        <h2 className="text-base font-bold text-slate-800 tracking-tight">
          GIS Map (North Eastern Region)
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
              <span className="text-[10px]">Landslide Heatmap</span>
            </div>
          </div>
        </div>

        {/* Floating Top-Right Search Tag Pill */}
        <div className="absolute top-3 right-3 z-[1000] flex items-center gap-1.5 bg-[#10b981]/90 backdrop-blur-md text-white text-[11px] font-semibold px-2.5 py-1 rounded-full shadow-md">
          <MapPin className="w-3 h-3 fill-white text-[#10b981]" />
          <span>Active IoT Stations</span>
          <button className="hover:bg-emerald-700/50 p-0.5 rounded-full ml-0.5">
            <X className="w-3 h-3" />
          </button>
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
