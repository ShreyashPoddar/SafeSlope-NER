import React, { useState, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, Polygon, Popup } from 'react-leaflet';
import { 
  ShieldCheck, 
  ArrowLeft, 
  PenTool, 
  Trash2, 
  Save, 
  X, 
  Sliders, 
  CheckCircle2, 
  Lock, 
  Unlock, 
  Plus, 
  Compass, 
  FileCheck
} from 'lucide-react';
import { GeotechControlPanel } from '../components/GeotechControlPanel';
import type { RiskPolygon } from '../types/dashboard';
import { getRiskZones } from '../api/risk';
import type { RiskZoneBackend } from '../api/risk';

interface GeotechWorkspaceProps {
  onBackToDashboard?: () => void;
  riskPolygons?: RiskPolygon[];
  onPublishRiskPolygons?: (polygons: RiskPolygon[]) => void;
}

// Initial seed polygons for NER Slope Zones
const initialPolygons: RiskPolygon[] = [
  {
    id: 'poly-1',
    name: 'NH-6 Milepost 44 Landslide Hazard Polygon',
    severity: 'LEVEL 2',
    instabilityScore: 78,
    primaryTrigger: 'Soil Saturation',
    coords: [
      [23.7320, 92.7120],
      [23.7350, 92.7180],
      [23.7310, 92.7230],
      [23.7270, 92.7160]
    ],
    lastUpdated: '10 mins ago',
    authorInfo: 'Geotech Officer #104'
  },
  {
    id: 'poly-2',
    name: 'Hunthar Veng Critical Subsidence Zone',
    severity: 'LEVEL 3',
    instabilityScore: 92,
    primaryTrigger: 'Tilt Acceleration',
    coords: [
      [23.7220, 92.7050],
      [23.7260, 92.7090],
      [23.7230, 92.7140],
      [23.7190, 92.7090]
    ],
    lastUpdated: '15 mins ago',
    authorInfo: 'Geotech Officer #104'
  },
  {
    id: 'poly-3',
    name: 'Sonapur Tunnel Slope Sector B',
    severity: 'LEVEL 1',
    instabilityScore: 45,
    primaryTrigger: 'Seismic Activity',
    coords: [
      [23.7400, 92.7250],
      [23.7440, 92.7300],
      [23.7410, 92.7350],
      [23.7370, 92.7290]
    ],
    lastUpdated: '1 hour ago',
    authorInfo: 'Geotech Officer #104'
  }
];

export const GeotechWorkspace: React.FC<GeotechWorkspaceProps> = ({ 
  onBackToDashboard, 
  riskPolygons,
  onPublishRiskPolygons 
}) => {
  const [mode, setMode] = useState<'live' | 'edit'>('edit');
  const [polygons, setPolygons] = useState<RiskPolygon[]>(riskPolygons || initialPolygons);
  const [selectedPolygonId, setSelectedPolygonId] = useState<string | null>('poly-1');
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(true);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Sync with parent-provided polygons (from App.tsx)
  React.useEffect(() => {
    if (riskPolygons && riskPolygons.length > 0) {
      setPolygons(riskPolygons);
    }
  }, [riskPolygons]);

  // Also fetch directly from backend risk-zones endpoint
  const fetchRiskZones = useCallback(async () => {
    try {
      const zones: RiskZoneBackend[] = await getRiskZones();
      if (zones.length > 0) {
        const mapped: RiskPolygon[] = zones.map((z, idx) => {
          // Backend zones don't carry polygon coords yet — use seed fallback coords
          const seed = initialPolygons[idx % initialPolygons.length];
          const severity: RiskPolygon['severity'] =
            z.current_risk === 'CRITICAL' || z.current_risk === 'HIGH' ? 'LEVEL 3'
            : z.current_risk === 'MODERATE' ? 'LEVEL 2' : 'LEVEL 1';
          return {
            id: String(z.id),
            name: z.zone_name,
            severity,
            instabilityScore: Math.round(z.ml_risk_pct ?? 50),
            primaryTrigger: 'Soil Saturation',
            coords: seed?.coords ?? [[23.7320, 92.7120],[23.7350, 92.7180],[23.7310, 92.7230],[23.7270, 92.7160]],
            lastUpdated: z.updated_at ? new Date(z.updated_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : 'Unknown',
            authorInfo: `Corridor: ${z.corridor_code}`,
          };
        });
        setPolygons(mapped);
        if (onPublishRiskPolygons) onPublishRiskPolygons(mapped);
      }
    } catch {
      // backend offline — keep seed data
    }
  }, [onPublishRiskPolygons]);

  useEffect(() => {
    fetchRiskZones();
    const id = setInterval(fetchRiskZones, 30_000);
    return () => clearInterval(id);
  }, [fetchRiskZones]);


  const selectedPolygon = polygons.find(p => p.id === selectedPolygonId) || null;

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  const getPolygonStyle = (severity: 'LEVEL 1' | 'LEVEL 2' | 'LEVEL 3', isSelected: boolean) => {
    let color = '#f59e0b';
    let fillColor = '#fbbf24';

    if (severity === 'LEVEL 2') {
      color = '#ea580c';
      fillColor = '#f97316';
    } else if (severity === 'LEVEL 3') {
      color = '#dc2626';
      fillColor = '#ef4444';
    }

    return {
      color: isSelected ? '#10b981' : color,
      weight: isSelected ? 3.5 : 2,
      fillColor,
      fillOpacity: isSelected ? 0.6 : 0.35,
      dashArray: isSelected ? '6, 6' : undefined
    };
  };

  const handleCreateNewPolygon = () => {
    const defaultCenter: [number, number] = [23.7300, 92.7200];
    const newId = `poly-${Date.now()}`;
    const newPoly: RiskPolygon = {
      id: newId,
      name: `NER Hazard Zone ${polygons.length + 1}`,
      severity: 'LEVEL 2',
      instabilityScore: 65,
      primaryTrigger: 'Soil Saturation',
      coords: [
        [defaultCenter[0] + 0.003, defaultCenter[1] - 0.003],
        [defaultCenter[0] + 0.005, defaultCenter[1] + 0.003],
        [defaultCenter[0] - 0.002, defaultCenter[1] + 0.004],
        [defaultCenter[0] - 0.004, defaultCenter[1] - 0.002]
      ],
      lastUpdated: 'Just Now',
      authorInfo: 'Geotech Officer #104'
    };
    const updated = [...polygons, newPoly];
    setPolygons(updated);
    if (onPublishRiskPolygons) onPublishRiskPolygons(updated);
    setSelectedPolygonId(newId);
    setIsDrawerOpen(true);
    showToast('New Risk Polygon added to GIS Map. Configure details in side drawer.');
  };

  const handleDeletePolygon = (id: string) => {
    const updated = polygons.filter(p => p.id !== id);
    setPolygons(updated);
    if (onPublishRiskPolygons) onPublishRiskPolygons(updated);
    if (selectedPolygonId === id) {
      setSelectedPolygonId(null);
      setIsDrawerOpen(false);
    }
    showToast('Risk Polygon deleted.');
  };

  const handleUpdatePolygon = (updatedPoly: RiskPolygon) => {
    const polyWithMeta = {
      ...updatedPoly,
      lastUpdated: 'Just Now',
      authorInfo: 'Geotech Officer #104'
    };
    const updated = polygons.map(p => p.id === polyWithMeta.id ? polyWithMeta : p);
    setPolygons(updated);
    if (onPublishRiskPolygons) onPublishRiskPolygons(updated);
    showToast(`Polygon "${updatedPoly.name}" updated successfully.`);
  };

  const handleSaveRiskMap = () => {
    if (onPublishRiskPolygons) {
      onPublishRiskPolygons(polygons);
    }
    showToast('GIS Risk Map saved & synchronized live with Command Dashboard!');
  };

  return (
    <div className="min-h-screen bg-slate-900/10 p-3 sm:p-6 space-y-4">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-20 right-6 z-[9999] flex items-center gap-3 bg-emerald-600 text-white px-5 py-3 rounded-2xl shadow-2xl backdrop-blur-md animate-bounce border border-white/20">
          <CheckCircle2 className="w-5 h-5 text-emerald-200 shrink-0" />
          <span className="text-sm font-semibold">{toastMessage}</span>
          <button onClick={() => setToastMessage(null)} className="ml-2 hover:bg-emerald-700 p-1 rounded-full">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Top Bar Header */}
      <div className="glass-panel-light rounded-3xl p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 border border-white/80 shadow-xl">
        <div className="flex items-center gap-3">
          {onBackToDashboard && (
            <button 
              onClick={onBackToDashboard}
              className="p-2.5 rounded-2xl bg-white/80 hover:bg-emerald-50 text-slate-700 hover:text-[#10b981] transition-all border border-slate-200 shadow-sm flex items-center gap-2 group"
            >
              <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
              <span className="text-xs font-bold hidden sm:inline">Dashboard</span>
            </button>
          )}
          
          <div className="w-10 h-10 rounded-2xl bg-[#10b981] text-white flex items-center justify-center shadow-lg shadow-emerald-500/20 shrink-0">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg sm:text-xl font-black text-slate-900 tracking-tight">
                Geotechnical & Meteorological Officer Workspace
              </h1>
              <span className="bg-emerald-100 text-[#10b981] text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full border border-emerald-300">
                Specialist Access
              </span>
            </div>
            <p className="text-xs text-slate-600 font-medium">
              Domain specialist access active • Interactive GIS Risk Boundary Calibration & Telemetry Override
            </p>
          </div>
        </div>

        {/* Mode Toggle Controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center bg-slate-200/80 p-1 rounded-2xl border border-slate-300 shadow-inner">
            <button
              onClick={() => setMode('live')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
                mode === 'live' 
                  ? 'bg-emerald-600 text-white shadow-md' 
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Lock className="w-3.5 h-3.5" />
              <span>Live Monitoring Mode</span>
            </button>
            <button
              onClick={() => setMode('edit')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
                mode === 'edit' 
                  ? 'bg-emerald-600 text-white shadow-md' 
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Unlock className="w-3.5 h-3.5" />
              <span>Edit & Calibration Mode</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Split Viewport Container (65% Map / 35% Control Panel) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Zone 1: Interactive GIS Map (65% width / lg:col-span-8) */}
        <div className="lg:col-span-8 glass-panel-emerald-glow rounded-3xl p-4 flex flex-col h-[760px] relative overflow-hidden">
          
          {/* GIS Map Header */}
          <div className="flex items-center justify-between mb-3 px-1">
            <div className="flex items-center gap-2">
              <Compass className="w-5 h-5 text-[#10b981]" />
              <h2 className="text-base font-bold text-slate-800 tracking-tight">
                Interactive GIS Risk Map (NER Slope Geometries)
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-500 bg-white/70 px-2.5 py-1 rounded-full border border-slate-200">
                Mode: <strong className="text-emerald-700 uppercase">{mode}</strong>
              </span>
            </div>
          </div>

          {/* Map Container */}
          <div className="relative flex-1 w-full rounded-2xl overflow-hidden shadow-inner border border-slate-200">
            
            {/* Top-Left Floating Map Drawing Toolbar */}
            <div className="absolute top-4 left-4 z-[1000] flex flex-wrap items-center gap-2 bg-white/95 backdrop-blur-md p-2 rounded-2xl shadow-xl border border-slate-200">
              <button
                onClick={handleCreateNewPolygon}
                disabled={mode === 'live'}
                className="flex items-center gap-1.5 bg-[#10b981] hover:bg-emerald-600 disabled:opacity-50 text-white text-xs font-bold px-3 py-2 rounded-xl shadow transition-all"
              >
                <Plus className="w-4 h-4" />
                <span>Draw Risk Polygon</span>
              </button>

              <button
                onClick={() => {
                  if (selectedPolygonId) setIsDrawerOpen(true);
                  else showToast('Please select a polygon on the map first.');
                }}
                disabled={!selectedPolygonId || mode === 'live'}
                className="flex items-center gap-1.5 bg-slate-100 hover:bg-slate-200 disabled:opacity-40 text-slate-700 text-xs font-semibold px-3 py-2 rounded-xl border border-slate-300 transition-all"
              >
                <PenTool className="w-3.5 h-3.5 text-slate-600" />
                <span>Edit Selected</span>
              </button>

              <button
                onClick={() => {
                  if (selectedPolygonId) handleDeletePolygon(selectedPolygonId);
                  else showToast('Please select a polygon to delete.');
                }}
                disabled={!selectedPolygonId || mode === 'live'}
                className="flex items-center gap-1.5 bg-rose-50 hover:bg-rose-100 disabled:opacity-40 text-rose-600 text-xs font-semibold px-3 py-2 rounded-xl border border-rose-200 transition-all"
              >
                <Trash2 className="w-3.5 h-3.5 text-rose-500" />
                <span>Delete</span>
              </button>

              <div className="h-4 w-px bg-slate-300 mx-1" />

              <button
                onClick={handleSaveRiskMap}
                className="flex items-center gap-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold px-3.5 py-2 rounded-xl shadow transition-all"
              >
                <Save className="w-3.5 h-3.5 text-emerald-400" />
                <span>Save Risk Map</span>
              </button>
            </div>

            {/* Top-Right Floating Legend */}
            <div className="absolute top-4 right-4 z-[1000] bg-white/90 backdrop-blur-md p-3 rounded-2xl shadow-lg border border-white/80 text-xs font-medium space-y-1.5 min-w-[170px]">
              <div className="font-bold text-slate-800 mb-1 border-b border-slate-200 pb-1 flex items-center justify-between">
                <span>Hazard Legend</span>
                <span className="text-[10px] text-slate-400 font-normal">3 Zones</span>
              </div>
              <div className="flex items-center gap-2 text-slate-700">
                <div className="w-3 h-3 rounded bg-amber-400 border border-amber-600 shrink-0" />
                <span className="text-[11px]">Level 1 (Alert)</span>
              </div>
              <div className="flex items-center gap-2 text-slate-700">
                <div className="w-3 h-3 rounded bg-orange-500 border border-orange-700 shrink-0" />
                <span className="text-[11px]">Level 2 (Evacuate)</span>
              </div>
              <div className="flex items-center gap-2 text-slate-700">
                <div className="w-3 h-3 rounded bg-rose-600 border border-rose-800 shrink-0" />
                <span className="text-[11px]">Level 3 (Critical Rescue)</span>
              </div>
            </div>

            {/* Leaflet Map rendering polygons */}
            <MapContainer
              center={[23.7310, 92.7176]}
              zoom={13}
              style={{ height: '100%', width: '100%' }}
              zoomControl={false}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              {polygons.map((poly) => {
                const isSelected = poly.id === selectedPolygonId;
                const style = getPolygonStyle(poly.severity, isSelected);

                return (
                  <Polygon
                    key={poly.id}
                    positions={poly.coords}
                    pathOptions={style}
                    eventHandlers={{
                      click: () => {
                        setSelectedPolygonId(poly.id);
                        setIsDrawerOpen(true);
                      }
                    }}
                  >
                    <Popup>
                      <div className="p-1 font-sans space-y-1.5 max-w-[200px]">
                        <div className="font-bold text-slate-900 text-xs">{poly.name}</div>
                        <div className="flex items-center gap-1.5 text-[11px]">
                          <span className="font-bold text-slate-500">Severity:</span>
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-black text-white ${
                            poly.severity === 'LEVEL 3' ? 'bg-rose-600' : poly.severity === 'LEVEL 2' ? 'bg-orange-500' : 'bg-amber-500'
                          }`}>
                            {poly.severity}
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-600">
                          Instability Score: <strong>{poly.instabilityScore}%</strong>
                        </div>
                        <div className="text-[11px] text-slate-600">
                          Trigger: <strong>{poly.primaryTrigger}</strong>
                        </div>
                        <button
                          onClick={() => {
                            setSelectedPolygonId(poly.id);
                            setIsDrawerOpen(true);
                          }}
                          className="w-full mt-2 bg-[#10b981] hover:bg-emerald-600 text-white text-[11px] font-bold py-1 rounded shadow transition-all"
                        >
                          Configure Zone
                        </button>
                      </div>
                    </Popup>
                  </Polygon>
                );
              })}
            </MapContainer>

            {/* Polygon Drawer (Slides in from bottom or overlay) */}
            {isDrawerOpen && selectedPolygon && (
              <div className="absolute top-0 right-0 bottom-0 z-[1001] w-full max-w-[360px] bg-white/95 backdrop-blur-xl border-l border-slate-200 shadow-2xl p-5 overflow-y-auto flex flex-col justify-between animate-in slide-in-from-right duration-300">
                <div className="space-y-4">
                  {/* Drawer Header */}
                  <div className="flex items-center justify-between pb-3 border-b border-slate-200">
                    <div className="flex items-center gap-2">
                      <Sliders className="w-5 h-5 text-[#10b981]" />
                      <h3 className="font-bold text-slate-900 text-sm">
                        Polygon Risk Configurator
                      </h3>
                    </div>
                    <button 
                      onClick={() => setIsDrawerOpen(false)}
                      className="text-slate-400 hover:text-slate-700 p-1 rounded-full hover:bg-slate-100 transition-all"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>

                  {/* Polygon ID badge */}
                  <div className="text-[11px] font-mono bg-slate-100 text-slate-600 px-2.5 py-1 rounded-lg border border-slate-200 flex justify-between">
                    <span>ID: {selectedPolygon.id}</span>
                    <span>{selectedPolygon.coords.length} Vertices</span>
                  </div>

                  {/* Input: Zone Name */}
                  <div className="space-y-1.5">
                    <label className="block text-xs font-bold text-slate-700">
                      Zone Name / Location Label
                    </label>
                    <input
                      type="text"
                      value={selectedPolygon.name}
                      disabled={mode === 'live'}
                      onChange={(e) => handleUpdatePolygon({ ...selectedPolygon, name: e.target.value })}
                      className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] focus:ring-2 focus:ring-[#10b981]/20 rounded-xl px-3 py-2 text-xs font-semibold text-slate-800 disabled:opacity-60"
                      placeholder="e.g. NH-6 Milepost 44 Landslide Polygon"
                    />
                  </div>

                  {/* Input: Hazard Severity */}
                  <div className="space-y-1.5">
                    <label className="block text-xs font-bold text-slate-700">
                      Hazard Severity Level
                    </label>
                    <select
                      value={selectedPolygon.severity}
                      disabled={mode === 'live'}
                      onChange={(e) => handleUpdatePolygon({ ...selectedPolygon, severity: e.target.value as any })}
                      className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] focus:ring-2 focus:ring-[#10b981]/20 rounded-xl px-3 py-2 text-xs font-bold text-slate-800 disabled:opacity-60"
                    >
                      <option value="LEVEL 1">Level 1 (Alert Status)</option>
                      <option value="LEVEL 2">Level 2 (Evacuate Advisories)</option>
                      <option value="LEVEL 3">Level 3 (Critical Rescue Zone)</option>
                    </select>
                  </div>

                  {/* Input: Instability Score Slider */}
                  <div className="space-y-2">
                    <div className="flex justify-between items-center text-xs font-bold text-slate-700">
                      <span>Instability Risk Index</span>
                      <span className={`px-2 py-0.5 rounded-full text-white text-[11px] font-black ${
                        selectedPolygon.instabilityScore > 80 ? 'bg-rose-600' : selectedPolygon.instabilityScore > 60 ? 'bg-orange-500' : 'bg-amber-500'
                      }`}>
                        {selectedPolygon.instabilityScore}%
                      </span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={selectedPolygon.instabilityScore}
                      disabled={mode === 'live'}
                      onChange={(e) => handleUpdatePolygon({ ...selectedPolygon, instabilityScore: Number(e.target.value) })}
                      className="w-full accent-[#10b981] cursor-pointer"
                    />
                    <div className="flex justify-between text-[10px] font-semibold text-slate-400">
                      <span>0% (Stable Slope)</span>
                      <span>50% (Moderate)</span>
                      <span>100% (Imminent Slide)</span>
                    </div>
                  </div>

                  {/* Input: Primary Trigger */}
                  <div className="space-y-1.5">
                    <label className="block text-xs font-bold text-slate-700">
                      Primary Geotechnical Trigger
                    </label>
                    <select
                      value={selectedPolygon.primaryTrigger}
                      disabled={mode === 'live'}
                      onChange={(e) => handleUpdatePolygon({ ...selectedPolygon, primaryTrigger: e.target.value as any })}
                      className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] focus:ring-2 focus:ring-[#10b981]/20 rounded-xl px-3 py-2 text-xs font-semibold text-slate-800 disabled:opacity-60"
                    >
                      <option value="Soil Saturation">Soil Saturation (Rainfall Pore Pressure)</option>
                      <option value="Tilt Acceleration">Tilt Acceleration (Sub-surface Creep)</option>
                      <option value="Seismic Activity">Seismic Activity (Micro-vibrations)</option>
                    </select>
                  </div>
                </div>

                {/* Drawer Footer Actions */}
                <div className="pt-4 border-t border-slate-200 space-y-2 mt-4">
                  <button
                    onClick={() => {
                      handleUpdatePolygon(selectedPolygon);
                      setIsDrawerOpen(false);
                    }}
                    className="w-full bg-[#10b981] hover:bg-emerald-600 text-white font-bold text-xs py-2.5 rounded-xl shadow transition-all flex items-center justify-center gap-2"
                  >
                    <FileCheck className="w-4 h-4" />
                    <span>Apply Zone Adjustments</span>
                  </button>
                  <button
                    onClick={() => handleDeletePolygon(selectedPolygon.id)}
                    disabled={mode === 'live'}
                    className="w-full bg-rose-50 hover:bg-rose-100 disabled:opacity-40 text-rose-600 font-bold text-xs py-2 rounded-xl border border-rose-200 transition-all flex items-center justify-center gap-2"
                  >
                    <Trash2 className="w-3.5 h-3.5 text-rose-500" />
                    <span>Remove Polygon</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Zone 2: Control & Telemetry Panel (35% width / lg:col-span-4) */}
        <div className="lg:col-span-4">
          <GeotechControlPanel />
        </div>

      </div>
    </div>
  );
};
