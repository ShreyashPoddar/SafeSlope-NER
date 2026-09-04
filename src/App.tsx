import { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { MapView } from './components/MapView';
import { TelemetryIndicators } from './components/TelemetryIndicators';
import { IsolationTwin } from './components/IsolationTwin';
import { IncidentQueue } from './components/IncidentQueue';
import { CitizenReport } from './pages/CitizenReport';
import { SOPDocumentPage } from './pages/SOPDocument';
import { AuthPage } from './pages/Auth';
import { GeotechWorkspace } from './pages/GeotechWorkspace';
import { IncidentModerationWorkspace } from './pages/IncidentModerationWorkspace';
import { DispatchCommandWorkspace } from './pages/DispatchCommandWorkspace';
import { FieldOperationsWorkspace } from './pages/FieldOperationsWorkspace';
import { SuperAdminWorkspace } from './pages/SuperAdminWorkspace';
import { ProtectedRoute } from './components/ProtectedRoute';
import { useAuth } from './hooks/useAuth.tsx';
import { getSensorHealth } from './api/telemetry';
import { getRiskState } from './api/risk';
import { listReports } from './api/reports';
import type { SensorHealth } from './api/telemetry';
import type { RiskStateEntry } from './api/risk';
import type {
  IoTNode,
  CitizenIncident,
  IsolationStats,
  RoadDisconnect,
  TelemetryData,
  UserProfile,
  RiskPolygon
} from './types/dashboard';

// Fallback/seed data shown when the backend is unreachable
const FALLBACK_IOT_NODES: IoTNode[] = [
  { id: 'iot-1', name: 'IoT Node 4 (Hunthar Veng Slope)', lat: 23.7380, lng: 92.7090, tiltChange: 4.8, moisture: 65, battery: 92, status: 'critical' },
  { id: 'iot-2', name: 'IoT Node 2 (Kolasib Sector)',     lat: 23.7210, lng: 92.7210, tiltChange: 1.2, moisture: 55, battery: 98, status: 'warning' },
  { id: 'iot-3', name: 'IoT Node 7 (Sonapur Ridge)',      lat: 23.7150, lng: 92.7310, tiltChange: 0.3, moisture: 35, battery: 89, status: 'normal' }
];

const FALLBACK_INCIDENTS: CitizenIncident[] = [
  { id: 'inc-101', reporterPhone: '+91 98625 11234', locationName: 'Hunthar Veng Junction', tag: 'Rockfall',  photoUrl: '/bg_rolling_hills.png', description: 'Boulders blocked primary lane near Hunthar Veng junction.', timestamp: '10 mins ago', lat: 23.7380, lng: 92.7090, status: 'pending',  confidence: 0.89 },
  { id: 'inc-102', reporterPhone: '+91 94361 88219', locationName: 'Sonapur Ridge Highway', tag: 'Mudslide', photoUrl: '/bg_rolling_hills.png', description: 'Soft soil slip across Sonapur Ridge.',                          timestamp: '25 mins ago', lat: 23.7150, lng: 92.7310, status: 'approved', confidence: 0.94 }
];

const FALLBACK_ISOLATION_STATS: IsolationStats = {
  isolatedPopulation: 12450, cutoffVillagesCount: 20, primaryCutoffRoad: 'NH-6 Sonapur Cut',
  estimatedClearingTimeHours: 18, strandedPhcCount: 4, detourKm: 42.5, delayMins: 85
};

const FALLBACK_ROAD_DISCONNECTS: RoadDisconnect[] = [
  { id: 'road-1', name: 'NH-6 Sonapur Cut',  route: 'NH-6 Corridor',  detourKm: 42.5, delayMins: 85, status: 'BLOCKED', lat: 23.7380, lng: 92.7090, affectedVillages: ['Hunthar', 'Sonapur', 'Kolasib'] },
  { id: 'road-2', name: 'NH-54 Aizawl Cut',  route: 'NH-54 Corridor', detourKm: 28.0, delayMins: 45, status: 'BLOCKED', lat: 23.7210, lng: 92.7210, affectedVillages: ['Zemabawk', 'Lunglei'] }
];

const FALLBACK_TELEMETRY: TelemetryData = {
  displacementMm: 4.8, displacementTrend: 'critical', moisturePercent: 65,
  rainfallMmHr: 42.5, seismicG: 0.18, threatLevel: 'LEVEL 4 CRITICAL'
};

const FALLBACK_RISK_POLYGONS: RiskPolygon[] = [
  { id: 'poly-1', name: 'NH-6 Milepost 44 Landslide Hazard Polygon', severity: 'LEVEL 2', instabilityScore: 78, primaryTrigger: 'Soil Saturation',  coords: [[23.7320,92.7120],[23.7350,92.7180],[23.7310,92.7230],[23.7270,92.7160]], lastUpdated: '10 mins ago',  authorInfo: 'Geotech Officer #104' },
  { id: 'poly-2', name: 'Hunthar Veng Critical Subsidence Zone',      severity: 'LEVEL 3', instabilityScore: 92, primaryTrigger: 'Tilt Acceleration', coords: [[23.7220,92.7050],[23.7260,92.7090],[23.7230,92.7140],[23.7190,92.7090]], lastUpdated: '15 mins ago',  authorInfo: 'Geotech Officer #104' },
  { id: 'poly-3', name: 'Sonapur Tunnel Slope Sector B',              severity: 'LEVEL 1', instabilityScore: 45, primaryTrigger: 'Seismic Activity',  coords: [[23.7400,92.7250],[23.7440,92.7300],[23.7410,92.7350],[23.7370,92.7290]], lastUpdated: '1 hour ago',    authorInfo: 'Geotech Officer #104' }
];

// Map backend SensorHealth[] to frontend IoTNode[]
function mapSensorsToIoTNodes(sensors: SensorHealth[]): IoTNode[] {
  return sensors.map((s, idx) => {
    const fallback = FALLBACK_IOT_NODES[idx % FALLBACK_IOT_NODES.length];
    const batteryPct = s.battery_soc_pct ?? (s.battery_v ? Math.round(((s.battery_v - 2.0) / 2.55) * 100) : null);
    const status: IoTNode['status'] =
      s.last_risk_level === 'CRITICAL' ? 'critical' : s.last_risk_level === 'HIGH' ? 'warning' : 'normal';
    return {
      id: s.sensor_id, name: `Sensor ${s.sensor_id}`,
      lat: fallback?.lat ?? 23.7380, lng: fallback?.lng ?? 92.7090,
      tiltChange: 0, moisture: 0,
      battery: batteryPct ?? undefined,
      status: s.active_status ? status : 'normal',
      lastUpdated: s.last_seen ?? undefined,
    };
  });
}

// Map backend RiskState to frontend TelemetryData
function mapRiskStateToTelemetry(riskState: Record<string, RiskStateEntry>): TelemetryData {
  const zones = Object.values(riskState);
  if (zones.length === 0) return FALLBACK_TELEMETRY;
  const worst = zones.reduce((a, b) => ((b.ml_risk_pct ?? 0) > (a.ml_risk_pct ?? 0) ? b : a));
  const riskPct = worst.ml_risk_pct ?? 50;
  return {
    displacementMm: worst.fos_value != null ? Math.round((2.0 - worst.fos_value) * 10 * 10) / 10 : 4.8,
    displacementTrend: riskPct >= 75 ? 'critical' : riskPct >= 50 ? 'rising' : 'stable',
    moisturePercent: FALLBACK_TELEMETRY.moisturePercent,
    rainfallMmHr: FALLBACK_TELEMETRY.rainfallMmHr,
    seismicG: FALLBACK_TELEMETRY.seismicG,
    threatLevel: worst.current_risk === 'CRITICAL' ? 'LEVEL 4 CRITICAL'
      : worst.current_risk === 'HIGH' ? 'LEVEL 3'
      : worst.current_risk === 'MODERATE' ? 'LEVEL 2' : 'LEVEL 1',
  };
}

// Map backend reports to frontend CitizenIncident[]
function mapReportsToIncidents(reports: Awaited<ReturnType<typeof listReports>>): CitizenIncident[] {
  return reports.map((r) => ({
    id: String(r.id), lat: r.latitude, lng: r.longitude,
    photoUrl: '/bg_rolling_hills.png',
    tag: r.ai_classification as CitizenIncident['tag'],
    confidence: r.ai_confidence_pct / 100,
    timestamp: new Date(r.submitted_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
    status: r.verified_by_volunteer ? 'approved' : 'pending',
  }));
}

function MainRoutes() {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentUser, logout } = useAuth();

  const [authRegisterMode, setAuthRegisterMode] = useState<boolean>(true);
  const [incidents, setIncidents]     = useState<CitizenIncident[]>(FALLBACK_INCIDENTS);
  const [riskPolygons, setRiskPolygons] = useState<RiskPolygon[]>(FALLBACK_RISK_POLYGONS);
  const [iotNodes, setIotNodes]       = useState<IoTNode[]>(FALLBACK_IOT_NODES);
  const [telemetry, setTelemetry]     = useState<TelemetryData>(FALLBACK_TELEMETRY);
  const [mapFocusCoords, setMapFocusCoords] = useState<[number, number] | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean>(false);

  // Live data polling
  const fetchLiveData = useCallback(async () => {
    try {
      const sensors = await getSensorHealth();
      if (sensors.length > 0) { setIotNodes(mapSensorsToIoTNodes(sensors)); setBackendOnline(true); }
    } catch { /* backend offline */ }
    try {
      const riskState = await getRiskState();
      setTelemetry(mapRiskStateToTelemetry(riskState));
    } catch { /* keep fallback */ }
    try {
      const reports = await listReports(20);
      if (reports.length > 0) setIncidents(mapReportsToIncidents(reports));
    } catch { /* keep fallback */ }
  }, []);

  useEffect(() => {
    fetchLiveData();
    const id = setInterval(fetchLiveData, 20_000);
    return () => clearInterval(id);
  }, [fetchLiveData]);

  const handleFocusMap = (lat: number, lng: number) => setMapFocusCoords([lat, lng]);
  const handleNewCitizenReport = (r: CitizenIncident) => setIncidents(prev => [r, ...prev]);
  const handleOpenAuth = (isRegisterMode: boolean) => { setAuthRegisterMode(isRegisterMode); navigate('/login'); };

  const handleLoginSuccess = (user: UserProfile | null) => {
    if (!user) return;
    setToastMessage(null);
    if (user.persona === 'head_admin') navigate('/admin/system');
    else if (user.subRole?.includes('Geotechnical')) navigate('/admin/geotech');
    else if (user.subRole?.includes('Incident')) navigate('/admin/moderation');
    else if (user.subRole?.includes('Dispatch') || user.subRole?.includes('DDMA')) navigate('/admin/dispatch');
    else if (user.subRole?.includes('First Responder') || user.subRole?.includes('Field Operations')) navigate('/admin/field-ops');
    else navigate('/');
  };

  const handleLogout = () => { logout(); navigate('/'); };
  const handleUnauthorizedToast = (msg: string) => setToastMessage(msg);

  return (
    <>
      {!backendOnline && (
        <div className="fixed bottom-4 left-4 z-[9998] bg-amber-900/90 backdrop-blur-md border border-amber-500 text-amber-100 px-3 py-2 rounded-lg text-xs font-semibold flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
          Offline mode — showing demo data
        </div>
      )}
      {toastMessage && (
        <div className="fixed top-4 right-4 z-[9999] bg-rose-900/95 backdrop-blur-md border border-rose-500 text-white px-4 py-3 rounded-xl shadow-2xl flex items-center justify-between gap-3 text-xs font-semibold">
          <span>{toastMessage}</span>
          <button onClick={() => setToastMessage(null)} className="text-rose-200 hover:text-white font-bold ml-2 cursor-pointer">✕</button>
        </div>
      )}

      <Routes>
        <Route path="/" element={
          <div className="min-h-screen p-4 lg:p-6 flex flex-col gap-5 max-w-[1920px] mx-auto">
            <Navbar currentPath={location.pathname} currentUser={currentUser} isolationStats={FALLBACK_ISOLATION_STATS}
              onNavigate={(path) => navigate(path)} onOpenAuth={handleOpenAuth} onLogout={handleLogout} />
            <main className="grid grid-cols-1 lg:grid-cols-12 gap-5 flex-1 items-stretch">
              <div className="lg:col-span-7"><MapView iotNodes={iotNodes} citizenIncidents={incidents} riskPolygons={riskPolygons} focusCoords={mapFocusCoords} /></div>
              <div className="lg:col-span-5"><TelemetryIndicators telemetry={telemetry} /></div>
              <div className="lg:col-span-5"><IsolationTwin stats={FALLBACK_ISOLATION_STATS} roadDisconnects={FALLBACK_ROAD_DISCONNECTS} onFocusMap={handleFocusMap} /></div>
              <div className="lg:col-span-7"><IncidentQueue incidents={incidents} onFocusMap={handleFocusMap} /></div>
            </main>
          </div>
        } />

        <Route path="/report" element={<CitizenReport onBackToDashboard={() => navigate('/')} onSubmitReport={handleNewCitizenReport} />} />
        <Route path="/sop"    element={<SOPDocumentPage stats={FALLBACK_ISOLATION_STATS} onBackToDashboard={() => navigate('/')} />} />
        <Route path="/login"  element={<AuthPage initialRegisterMode={authRegisterMode} onBackToDashboard={() => navigate('/')} onLoginSuccess={handleLoginSuccess} onEmergencyReport={() => navigate('/report')} />} />

        <Route path="/admin/geotech" element={
          <ProtectedRoute currentUser={currentUser} allowedRoles={['Geotechnical & Meteorological Officer']} onUnauthorizedToast={handleUnauthorizedToast}>
            <GeotechWorkspace onBackToDashboard={() => navigate('/')} riskPolygons={riskPolygons} onPublishRiskPolygons={(u) => setRiskPolygons(u)} />
          </ProtectedRoute>
        } />

        <Route path="/admin/moderation" element={
          <ProtectedRoute currentUser={currentUser} allowedRoles={['Incident Moderation & Citizen Report Admin']} onUnauthorizedToast={handleUnauthorizedToast}>
            <IncidentModerationWorkspace onBackToDashboard={() => navigate('/')} onApproveIncident={(a) => setIncidents(prev => [a, ...prev])} />
          </ProtectedRoute>
        } />

        <Route path="/admin/dispatch" element={
          <ProtectedRoute currentUser={currentUser} allowedRoles={['Emergency Dispatch & DDMA Nodal Officer']} onUnauthorizedToast={handleUnauthorizedToast}>
            <DispatchCommandWorkspace onBackToDashboard={() => navigate('/')} onNavigateToSOP={() => navigate('/sop')} />
          </ProtectedRoute>
        } />

        <Route path="/admin/field-ops" element={
          <ProtectedRoute currentUser={currentUser} allowedRoles={['First Responder / Field Operations Officer']} onUnauthorizedToast={handleUnauthorizedToast}>
            <FieldOperationsWorkspace onBackToDashboard={() => navigate('/')} />
          </ProtectedRoute>
        } />

        <Route path="/admin/system" element={
          <ProtectedRoute currentUser={currentUser} requireHeadAdmin={true} onUnauthorizedToast={handleUnauthorizedToast}>
            <SuperAdminWorkspace currentUser={currentUser} onBackToDashboard={() => navigate('/')} />
          </ProtectedRoute>
        } />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <MainRoutes />
    </BrowserRouter>
  );
}

export default App;
