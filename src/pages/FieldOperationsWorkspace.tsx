import React, { useState } from 'react';
import { 
  Truck, 
  ArrowLeft, 
  Wifi, 
  WifiOff, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Users, 
  MapPin, 
  X
} from 'lucide-react';
import { FieldResourcePanel } from '../components/FieldResourcePanel';
import type { RouteStatus, FieldResourceState } from '../types/dashboard';

interface FieldOperationsWorkspaceProps {
  onBackToDashboard?: () => void;
  onUpdateCorridorState?: (corridorId: string, state: RouteStatus['state']) => void;
}

// Initial mock route corridor states
const initialRoutes: RouteStatus[] = [
  {
    id: 'route-1',
    name: 'NH-6 Sonapur Cut Corridor',
    corridor: 'NH-6 Sector',
    state: 'SEVERED',
    clearanceNotes: '1 Excavator & BRO team deployed; clearing estimated at 14:00 IST',
    lastUpdated: '10 mins ago'
  },
  {
    id: 'route-2',
    name: 'SH-12 Bypass Route',
    corridor: 'SH-12 Sector',
    state: 'DETOUR',
    clearanceNotes: 'Single-lane traffic active for light emergency vehicles only',
    lastUpdated: '25 mins ago'
  },
  {
    id: 'route-3',
    name: 'NH-54 Aizawl Corridor',
    corridor: 'NH-54 Sector',
    state: 'CLEAR',
    clearanceNotes: 'Open for all traffic; minor wet surface slip watch',
    lastUpdated: '45 mins ago'
  }
];

export const FieldOperationsWorkspace: React.FC<FieldOperationsWorkspaceProps> = ({
  onBackToDashboard,
  onUpdateCorridorState
}) => {
  // Connectivity Mode State
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const [queuedChangesCount, setQueuedChangesCount] = useState<number>(0);

  // Card 1: Route Corridor Status State
  const [routes, setRoutes] = useState<RouteStatus[]>(initialRoutes);

  // Card 2: Personnel & Heavy Machinery Tally State
  const [personnel, setPersonnel] = useState({
    ndrf: 4,
    sdrf: 6,
    bro: 12,
    police: 8
  });

  const [machinery, setMachinery] = useState({
    excavators: 2,
    earthmovers: 1,
    bulldozers: 1,
    ambulances: 3
  });

  const [machineryStatus, setMachineryStatus] = useState<'Operational' | 'Requires Fuel/Maintenance'>('Operational');

  // Card 3: Supply Inventory State
  const [resourceState, setResourceState] = useState<FieldResourceState>({
    personnel,
    machinery,
    machineryStatus: 'Operational',
    medicalSupplies: 'Sufficient',
    rations: 'Sufficient',
    satellitePhone: 'Active'
  });

  // Toast Notification State
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Route State Update Handler
  const handleRouteChange = (id: string, newState: RouteStatus['state']) => {
    setRoutes(prev => prev.map(r => r.id === id ? { ...r, state: newState, lastUpdated: 'Just now' } : r));

    if (!isOnline) {
      setQueuedChangesCount(prev => prev + 1);
      showToast(`[Offline Mode] Route ${id} updated to ${newState}. Changes queued for auto-sync.`);
    } else {
      showToast(`Route ${id} updated to ${newState} & synced to Command Dashboard!`);
    }

    if (onUpdateCorridorState) {
      onUpdateCorridorState(id, newState);
    }
  };

  // Clearance Notes Change Handler
  const handleNotesChange = (id: string, notes: string) => {
    setRoutes(prev => prev.map(r => r.id === id ? { ...r, clearanceNotes: notes } : r));
  };

  // Counter Tally Handlers
  const adjustPersonnel = (key: keyof typeof personnel, delta: number) => {
    setPersonnel(prev => {
      const val = Math.max(0, prev[key] + delta);
      return { ...prev, [key]: val };
    });
  };

  const adjustMachinery = (key: keyof typeof machinery, delta: number) => {
    setMachinery(prev => {
      const val = Math.max(0, prev[key] + delta);
      return { ...prev, [key]: val };
    });
  };

  // Connectivity Mode Toggle
  const toggleConnectivity = () => {
    if (!isOnline) {
      // Switching from Offline -> Online
      setIsOnline(true);
      if (queuedChangesCount > 0) {
        showToast(`🟢 Reconnected! ${queuedChangesCount} queued changes synchronized with Command Dashboard.`);
        setQueuedChangesCount(0);
      } else {
        showToast('🟢 Connectivity restored: Live Sync active.');
      }
    } else {
      setIsOnline(false);
      showToast('🟡 Offline Mode activated: Low-bandwidth change queueing enabled.');
    }
  };

  // GPS Ping Handler
  const handlePingGPS = (coords: [number, number]) => {
    showToast(`📍 Field Unit GPS Ping transmitted: [${coords[0].toFixed(4)}, ${coords[1].toFixed(4)}]. Responder marker updated on map!`);
  };

  return (
    <div className="min-h-screen bg-slate-900/10 p-3 sm:p-6 space-y-4 font-sans">
      
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

      {/* Top Banner & Connectivity Mode Switcher */}
      <div className="glass-panel-light rounded-3xl p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 border border-white/80 shadow-xl">
        <div className="flex items-center gap-3">
          {onBackToDashboard && (
            <button 
              onClick={onBackToDashboard}
              className="p-2.5 rounded-2xl bg-white/80 hover:bg-emerald-50 text-slate-700 hover:text-[#10b981] transition-all border border-slate-200 shadow-sm flex items-center gap-2 group cursor-pointer"
            >
              <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
              <span className="text-xs font-bold hidden sm:inline">Dashboard</span>
            </button>
          )}

          <div className="w-10 h-10 rounded-2xl bg-[#10b981] text-white flex items-center justify-center shadow-lg shadow-emerald-500/30 shrink-0">
            <Truck className="w-6 h-6" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg sm:text-xl font-black text-slate-900 tracking-tight">
                Field Operations Unit
              </h1>
              <span className="bg-emerald-100 text-[#10b981] text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full border border-emerald-300">
                Sector Command
              </span>
            </div>
            <p className="text-xs text-slate-600 font-medium">
              Touchscreen Mobile-Optimized Field Resource Management &amp; Corridor Status Tally
            </p>
          </div>
        </div>

        {/* CONNECTIVITY INDICATOR MODE TOGGLE */}
        <div className="flex items-center gap-3">
          
          {queuedChangesCount > 0 && (
            <span className="bg-amber-500 text-white font-mono text-[10px] font-extrabold px-2.5 py-1 rounded-full animate-pulse">
              {queuedChangesCount} Queued
            </span>
          )}

          <button
            onClick={toggleConnectivity}
            className={`px-4 py-2 rounded-2xl text-xs font-extrabold shadow-md transition-all cursor-pointer flex items-center gap-2 border ${
              isOnline
                ? 'bg-emerald-600 text-white border-emerald-400 shadow-emerald-600/20'
                : 'bg-amber-500 text-white border-amber-400 shadow-amber-500/20'
            }`}
          >
            {isOnline ? (
              <>
                <Wifi className="w-4 h-4 text-emerald-200" />
                <span>🟢 Online - Live Sync</span>
              </>
            ) : (
              <>
                <WifiOff className="w-4 h-4 text-amber-100 animate-pulse" />
                <span>🟡 Offline Mode - Changes Queued</span>
              </>
            )}
          </button>

        </div>
      </div>

      {/* Primary Touch-Friendly 3-Card Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* CARD 1 (Left / lg:col-span-4): Transport Route Availability Status Manager */}
        <div className="lg:col-span-4 glass-panel-light rounded-3xl p-5 flex flex-col justify-between h-[720px] border border-white/80 shadow-xl space-y-4">
          <div className="space-y-4">
            
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-slate-900 text-emerald-400 flex items-center justify-center font-bold">
                  <MapPin className="w-4 h-4 text-[#10b981]" />
                </div>
                <div>
                  <h3 className="text-sm font-black text-slate-900 tracking-tight">
                    Transport Corridor Status Manager
                  </h3>
                  <p className="text-[10px] text-slate-500 font-mono">
                    Real-time Corridor Clearance Tally
                  </p>
                </div>
              </div>
            </div>

            {/* Corridor List */}
            <div className="space-y-4 max-h-[560px] overflow-y-auto pr-1">
              {routes.map((rt) => (
                <div 
                  key={rt.id} 
                  className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-extrabold text-slate-900 text-xs">{rt.name}</h4>
                      <span className="text-[10px] text-slate-400 font-mono">Updated {rt.lastUpdated}</span>
                    </div>
                  </div>

                  {/* Touch State Buttons Grid */}
                  <div className="grid grid-cols-3 gap-1.5">
                    
                    {/* CLEAR */}
                    <button
                      onClick={() => handleRouteChange(rt.id, 'CLEAR')}
                      className={`py-2 px-1 rounded-xl text-[10px] font-black transition-all cursor-pointer flex flex-col items-center gap-1 border ${
                        rt.state === 'CLEAR'
                          ? 'bg-emerald-600 text-white border-emerald-500 shadow-md ring-2 ring-emerald-300'
                          : 'bg-emerald-50/60 text-emerald-800 border-emerald-200 hover:bg-emerald-100'
                      }`}
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>CLEAR / OPEN</span>
                    </button>

                    {/* DETOUR */}
                    <button
                      onClick={() => handleRouteChange(rt.id, 'DETOUR')}
                      className={`py-2 px-1 rounded-xl text-[10px] font-black transition-all cursor-pointer flex flex-col items-center gap-1 border ${
                        rt.state === 'DETOUR'
                          ? 'bg-amber-500 text-white border-amber-400 shadow-md ring-2 ring-amber-300'
                          : 'bg-amber-50/60 text-amber-900 border-amber-200 hover:bg-amber-100'
                      }`}
                    >
                      <AlertTriangle className="w-3.5 h-3.5" />
                      <span>DETOUR ACTIVE</span>
                    </button>

                    {/* SEVERED */}
                    <button
                      onClick={() => handleRouteChange(rt.id, 'SEVERED')}
                      className={`py-2 px-1 rounded-xl text-[10px] font-black transition-all cursor-pointer flex flex-col items-center gap-1 border ${
                        rt.state === 'SEVERED'
                          ? 'bg-rose-600 text-white border-rose-500 shadow-md ring-2 ring-rose-300 animate-pulse'
                          : 'bg-rose-50/60 text-rose-800 border-rose-200 hover:bg-rose-100'
                      }`}
                    >
                      <XCircle className="w-3.5 h-3.5" />
                      <span>SEVERED</span>
                    </button>

                  </div>

                  {/* Inline Clearance Notes & ETA */}
                  <div className="space-y-1">
                    <label className="block text-[10px] font-bold text-slate-500 uppercase">Clearance Notes / ETA</label>
                    <input
                      type="text"
                      value={rt.clearanceNotes}
                      onChange={(e) => handleNotesChange(rt.id, e.target.value)}
                      className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] rounded-xl px-2.5 py-1.5 text-xs font-semibold text-slate-800"
                    />
                  </div>

                </div>
              ))}
            </div>

          </div>
        </div>

        {/* CARD 2 (Center / lg:col-span-4): On-Site Personnel & Heavy Machinery Tracker */}
        <div className="lg:col-span-4 glass-panel-light rounded-3xl p-5 flex flex-col justify-between h-[720px] border border-white/80 shadow-xl space-y-4">
          <div className="space-y-4">
            
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-slate-900 text-emerald-400 flex items-center justify-center font-bold">
                  <Users className="w-4 h-4 text-[#10b981]" />
                </div>
                <div>
                  <h3 className="text-sm font-black text-slate-900 tracking-tight">
                    On-Site Personnel &amp; Heavy Machinery
                  </h3>
                  <p className="text-[10px] text-slate-500 font-mono">
                    Touch Tally &amp; Equipment Maintenance
                  </p>
                </div>
              </div>
            </div>

            {/* Personnel Counters Tally */}
            <div className="p-3.5 rounded-2xl bg-white/80 border border-slate-200 shadow-sm space-y-3">
              <span className="text-[11px] font-extrabold text-slate-800 uppercase tracking-wider block">
                Active Field Personnel Tally
              </span>

              <div className="grid grid-cols-2 gap-2.5">
                
                {/* NDRF */}
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-bold text-slate-900 block">NDRF Teams</span>
                    <span className="text-[10px] text-slate-400 font-mono">Rescue Unit</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button 
                      onClick={() => adjustPersonnel('ndrf', -1)} 
                      className="w-7 h-7 rounded-lg bg-slate-200 hover:bg-slate-300 font-black text-slate-800 text-sm flex items-center justify-center cursor-pointer active:scale-95"
                    >
                      -
                    </button>
                    <span className="w-6 text-center font-mono font-black text-sm text-slate-900">{personnel.ndrf}</span>
                    <button 
                      onClick={() => adjustPersonnel('ndrf', 1)} 
                      className="w-7 h-7 rounded-lg bg-[#10b981] hover:bg-emerald-600 font-black text-white text-sm flex items-center justify-center cursor-pointer active:scale-95"
                    >
                      +
                    </button>
                  </div>
                </div>

                {/* SDRF */}
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-bold text-slate-900 block">SDRF Responders</span>
                    <span className="text-[10px] text-slate-400 font-mono">State Task force</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button 
                      onClick={() => adjustPersonnel('sdrf', -1)} 
                      className="w-7 h-7 rounded-lg bg-slate-200 hover:bg-slate-300 font-black text-slate-800 text-sm flex items-center justify-center cursor-pointer active:scale-95"
                    >
                      -
                    </button>
                    <span className="w-6 text-center font-mono font-black text-sm text-slate-900">{personnel.sdrf}</span>
                    <button 
                      onClick={() => adjustPersonnel('sdrf', 1)} 
                      className="w-7 h-7 rounded-lg bg-[#10b981] hover:bg-emerald-600 font-black text-white text-sm flex items-center justify-center cursor-pointer active:scale-95"
                    >
                      +
                    </button>
                  </div>
                </div>

                {/* BRO Engineers */}
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-bold text-slate-900 block">BRO Engineers</span>
                    <span className="text-[10px] text-slate-400 font-mono">Highway Ops</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button 
                      onClick={() => adjustPersonnel('bro', -1)} 
                      className="w-7 h-7 rounded-lg bg-slate-200 hover:bg-slate-300 font-black text-slate-800 text-sm flex items-center justify-center cursor-pointer active:scale-95"
                    >
                      -
                    </button>
                    <span className="w-6 text-center font-mono font-black text-sm text-slate-900">{personnel.bro}</span>
                    <button 
                      onClick={() => adjustPersonnel('bro', 1)} 
                      className="w-7 h-7 rounded-lg bg-[#10b981] hover:bg-emerald-600 font-black text-white text-sm flex items-center justify-center cursor-pointer active:scale-95"
                    >
                      +
                    </button>
                  </div>
                </div>

                {/* Local Police */}
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-bold text-slate-900 block">Local Police</span>
                    <span className="text-[10px] text-slate-400 font-mono">Traffic Control</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button 
                      onClick={() => adjustPersonnel('police', -1)} 
                      className="w-7 h-7 rounded-lg bg-slate-200 hover:bg-slate-300 font-black text-slate-800 text-sm flex items-center justify-center cursor-pointer active:scale-95"
                    >
                      -
                    </button>
                    <span className="w-6 text-center font-mono font-black text-sm text-slate-900">{personnel.police}</span>
                    <button 
                      onClick={() => adjustPersonnel('police', 1)} 
                      className="w-7 h-7 rounded-lg bg-[#10b981] hover:bg-emerald-600 font-black text-white text-sm flex items-center justify-center cursor-pointer active:scale-95"
                    >
                      +
                    </button>
                  </div>
                </div>

              </div>
            </div>

            {/* Heavy Machinery Deployed Tally */}
            <div className="p-3.5 rounded-2xl bg-white/80 border border-slate-200 shadow-sm space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-[11px] font-extrabold text-slate-800 uppercase tracking-wider">
                  Heavy Machinery &amp; Ambulances
                </span>

                {/* Machinery Maintenance Status Toggle */}
                <button
                  onClick={() => setMachineryStatus(machineryStatus === 'Operational' ? 'Requires Fuel/Maintenance' : 'Operational')}
                  className={`px-2 py-0.5 rounded-full text-[10px] font-black transition-all cursor-pointer ${
                    machineryStatus === 'Operational' ? 'bg-emerald-100 text-emerald-900 border border-emerald-300' : 'bg-rose-100 text-rose-900 border border-rose-300'
                  }`}
                >
                  {machineryStatus}
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                
                {/* Excavators */}
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900">Excavators</span>
                  <div className="flex items-center gap-1.5">
                    <button 
                      onClick={() => adjustMachinery('excavators', -1)} 
                      className="w-7 h-7 rounded-lg bg-slate-200 hover:bg-slate-300 font-black text-slate-800 text-sm flex items-center justify-center cursor-pointer active:scale-95"
                    >
                      -
                    </button>
                    <span className="w-6 text-center font-mono font-black text-sm text-slate-900">{machinery.excavators}</span>
                    <button 
                      onClick={() => adjustMachinery('excavators', 1)} 
                      className="w-7 h-7 rounded-lg bg-[#10b981] hover:bg-emerald-600 font-black text-white text-sm flex items-center justify-center cursor-pointer active:scale-95"
                    >
                      +
                    </button>
                  </div>
                </div>

                {/* Ambulances */}
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900">Ambulances</span>
                  <div className="flex items-center gap-1.5">
                    <button 
                      onClick={() => adjustMachinery('ambulances', -1)} 
                      className="w-7 h-7 rounded-lg bg-slate-200 hover:bg-slate-300 font-black text-slate-800 text-sm flex items-center justify-center cursor-pointer active:scale-95"
                    >
                      -
                    </button>
                    <span className="w-6 text-center font-mono font-black text-sm text-slate-900">{machinery.ambulances}</span>
                    <button 
                      onClick={() => adjustMachinery('ambulances', 1)} 
                      className="w-7 h-7 rounded-lg bg-[#10b981] hover:bg-emerald-600 font-black text-white text-sm flex items-center justify-center cursor-pointer active:scale-95"
                    >
                      +
                    </button>
                  </div>
                </div>

              </div>
            </div>

          </div>
        </div>

        {/* CARD 3 (Right / lg:col-span-4): Essential Emergency Supply & Field GPS Transceiver */}
        <div className="lg:col-span-4 h-[720px]">
          <FieldResourcePanel 
            resourceState={resourceState}
            onUpdateSupplies={(med, rat, sat) => {
              setResourceState(prev => ({ ...prev, medicalSupplies: med, rations: rat, satellitePhone: sat }));
              showToast('Emergency Supply Stock level updated.');
            }}
            onPingGPS={handlePingGPS}
          />
        </div>

      </div>

    </div>
  );
};
