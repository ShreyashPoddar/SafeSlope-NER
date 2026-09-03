import { useState } from 'react';
import { Activity, LayoutDashboard, Smartphone, FileText } from 'lucide-react';
import { MapView } from './components/MapView';
import { TelemetryIndicators } from './components/TelemetryIndicators';
import { IsolationTwin } from './components/IsolationTwin';
import { IncidentQueue } from './components/IncidentQueue';
import { DownloadSOPButton } from './components/SOPDocument';
import { CitizenReport } from './pages/CitizenReport';
import { SOPDocumentPage } from './pages/SOPDocument';
import type { 
  IoTNode, 
  CitizenIncident, 
  IsolationStats, 
  RoadDisconnect, 
  TelemetryData 
} from './types/dashboard';

// Initial Mock Data - North Eastern India (NER) Context (Mizoram / Meghalaya Hill Corridor)
const INITIAL_IOT_NODES: IoTNode[] = [
  {
    id: 'iot-1',
    name: 'IoT Node 4 (Hunthar Veng Slope)',
    lat: 23.7380,
    lng: 92.7090,
    tiltChange: 4.8,
    moisture: 65,
    battery: 92,
    status: 'critical'
  },
  {
    id: 'iot-2',
    name: 'IoT Node 2 (Kolasib Sector)',
    lat: 23.7210,
    lng: 92.7210,
    tiltChange: 1.2,
    moisture: 55,
    battery: 98,
    status: 'warning'
  },
  {
    id: 'iot-3',
    name: 'IoT Node 7 (Sonapur Ridge)',
    lat: 23.7150,
    lng: 92.7310,
    tiltChange: 0.3,
    moisture: 42,
    battery: 89,
    status: 'normal'
  }
];

const INITIAL_INCIDENTS: CitizenIncident[] = [
  {
    id: 'inc-101',
    lat: 23.7350,
    lng: 92.7050,
    photoUrl: 'https://images.unsplash.com/photo-1541888946425-d0fbb186a5b3?auto=format&fit=crop&w=600&q=80',
    tag: 'Rockfall',
    confidence: 0.942,
    timestamp: '14:22 IST',
    status: 'pending',
    locationName: 'NH-6 Sonapur Cut'
  },
  {
    id: 'inc-102',
    lat: 23.7250,
    lng: 92.7150,
    photoUrl: 'https://images.unsplash.com/photo-1517649763962-0c623266010b?auto=format&fit=crop&w=600&q=80',
    tag: 'Road Crack',
    confidence: 0.887,
    timestamp: '14:05 IST',
    status: 'pending',
    locationName: 'NH-54 Aizawl Cut'
  },
  {
    id: 'inc-103',
    lat: 23.7100,
    lng: 92.7250,
    photoUrl: 'https://images.unsplash.com/photo-1508873696983-2df5057c0256?auto=format&fit=crop&w=600&q=80',
    tag: 'Mudslide',
    confidence: 0.965,
    timestamp: '13:48 IST',
    status: 'approved',
    locationName: 'Kolasib Access Road'
  }
];

const INITIAL_ISOLATION_STATS: IsolationStats = {
  isolatedPopulation: 12450,
  cutoffVillagesCount: 20,
  primaryCutoffRoad: 'NH-6 Sonapur Cut',
  estimatedClearingTimeHours: 18,
  strandedPhcCount: 4,
  detourKm: 42.5,
  delayMins: 85
};

const INITIAL_ROAD_DISCONNECTS: RoadDisconnect[] = [
  {
    id: 'road-1',
    name: 'NH-6 Sonapur Cut',
    route: 'Asymmetrical barrier units',
    detourKm: 42.5,
    delayMins: 85,
    status: 'BLOCKED',
    lat: 23.7380,
    lng: 92.7090,
    affectedVillages: ['Hunthar', 'Sonapur']
  },
  {
    id: 'road-2',
    name: 'NH-54 Aizawl ...',
    route: 'Asymmetrical under cards',
    detourKm: 18,
    delayMins: 35,
    status: 'IMPASSABLE',
    lat: 23.7210,
    lng: 92.7210,
    affectedVillages: ['Kolasib S-4']
  }
];

const INITIAL_TELEMETRY: TelemetryData = {
  displacementMm: 4.8,
  displacementTrend: 'critical',
  moisturePercent: 65,
  rainfallMmHr: 42.5,
  seismicG: 0.18,
  threatLevel: 'LEVEL 4 CRITICAL'
};

export function App() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'report' | 'sop'>('dashboard');
  const [incidents, setIncidents] = useState<CitizenIncident[]>(INITIAL_INCIDENTS);
  const [mapFocusCoords, setMapFocusCoords] = useState<[number, number] | null>(null);

  const handleFocusMap = (lat: number, lng: number) => {
    setMapFocusCoords([lat, lng]);
  };

  const handleNewCitizenReport = (newReport: CitizenIncident) => {
    setIncidents(prev => [newReport, ...prev]);
  };

  // If in Citizen Report View
  if (currentView === 'report') {
    return (
      <CitizenReport 
        onBackToDashboard={() => setCurrentView('dashboard')} 
        onSubmitReport={handleNewCitizenReport}
      />
    );
  }

  // If in SOP Emergency Order Document View
  if (currentView === 'sop') {
    return (
      <SOPDocumentPage 
        stats={INITIAL_ISOLATION_STATS}
        onBackToDashboard={() => setCurrentView('dashboard')}
      />
    );
  }

  return (
    <div className="min-h-screen p-4 lg:p-6 flex flex-col gap-5 max-w-[1920px] mx-auto">
      
      {/* 1. Glass Header Bar (Top Navigation) */}
      <header className="flex flex-wrap items-center justify-between gap-4 py-1.5 px-1">
        
        {/* Left: Minimalist Mountain/Slope Emblem + SafeSlope Title */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-emerald-400/20 flex items-center justify-center text-emerald-300">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="m8 3 4 8 5-5 15H2L8 3z"/>
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight font-sans drop-shadow-sm">
            SafeSlope
          </h1>
        </div>

        {/* Center: Live Status Pulse + View Navigation Buttons */}
        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-2 px-4 py-1.5 rounded-full glass-pill text-slate-800 text-xs font-semibold">
            <Activity className="w-4 h-4 text-[#10b981] animate-pulse" />
            <span>Live Status Pulse</span>
          </div>

          {/* Navigation Toggle: Dashboard vs Citizen Report vs SOP Order */}
          <div className="flex items-center p-1 rounded-full glass-pill text-xs font-semibold">
            <button
              onClick={() => setCurrentView('dashboard')}
              className="flex items-center gap-1.5 px-3 py-1 rounded-full transition-all cursor-pointer bg-[#10b981] text-white shadow-sm"
            >
              <LayoutDashboard className="w-3.5 h-3.5" />
              <span>Command Grid</span>
            </button>
            
            <button
              onClick={() => setCurrentView('report')}
              className="flex items-center gap-1.5 px-3 py-1 rounded-full transition-all cursor-pointer text-slate-700 hover:text-slate-900 hover:bg-white/50"
            >
              <Smartphone className="w-3.5 h-3.5" />
              <span>Report Hazard</span>
            </button>

            <button
              onClick={() => setCurrentView('sop')}
              className="flex items-center gap-1.5 px-3 py-1 rounded-full transition-all cursor-pointer text-slate-700 hover:text-slate-900 hover:bg-white/50"
            >
              <FileText className="w-3.5 h-3.5 text-emerald-700" />
              <span>SOP Order</span>
            </button>
          </div>
        </div>

        {/* Right: Solid Emerald Green Action Button -> Opens SOP View */}
        <div>
          <DownloadSOPButton stats={INITIAL_ISOLATION_STATS} onClick={() => setCurrentView('sop')} />
        </div>

      </header>

      {/* 2. Symmetric Bento Grid Layout */}
      <main className="grid grid-cols-12 gap-5 flex-1 items-stretch">
        
        {/* Row 1, Left: GIS Map Viewport (Top Left — 7 cols x 390px) */}
        <section className="col-span-12 lg:col-span-7 h-[390px]">
          <MapView 
            iotNodes={INITIAL_IOT_NODES} 
            citizenIncidents={incidents}
            focusCoords={mapFocusCoords}
          />
        </section>

        {/* Row 1, Right: Telemetry Analytics Panel (Top Right — 5 cols x 390px) */}
        <section className="col-span-12 lg:col-span-5 h-[390px]">
          <TelemetryIndicators telemetry={INITIAL_TELEMETRY} />
        </section>

        {/* Row 2, Left: Critical Isolation Impact Panel (Bottom Left — 5 cols x 390px) */}
        <section className="col-span-12 lg:col-span-5 h-[390px]">
          <IsolationTwin 
            stats={INITIAL_ISOLATION_STATS}
            roadDisconnects={INITIAL_ROAD_DISCONNECTS}
            onFocusMap={handleFocusMap}
          />
        </section>

        {/* Row 2, Right: Citizen Incident Moderation Queue (Bottom Right — 7 cols x 390px) */}
        <section className="col-span-12 lg:col-span-7 h-[390px]">
          <IncidentQueue 
            incidents={incidents}
            onFocusMap={handleFocusMap}
          />
        </section>

      </main>

    </div>
  );
}

export default App;
