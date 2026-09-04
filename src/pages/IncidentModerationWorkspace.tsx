import React, { useState, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import { 
  ShieldCheck, 
  ArrowLeft, 
  MapPin, 
  User, 
  Compass, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  GitMerge, 
  Phone, 
  Maximize2, 
  FileCheck2, 
  Check, 
  X,
  History,
  Info
} from 'lucide-react';
import { ModerationQueuePanel } from '../components/ModerationQueuePanel';
import type { CitizenIncident } from '../types/dashboard';
import { listReports } from '../api/reports';

interface IncidentModerationWorkspaceProps {
  onBackToDashboard?: () => void;
  onApproveIncident?: (incident: CitizenIncident) => void;
}

// Initial mock incidents for Zone 4 Ingestion Queue
const initialModerationIncidents: CitizenIncident[] = [
  {
    id: 'INC-2026-SL087',
    lat: 23.7380,
    lng: 92.7090,
    photoUrl: '/bg_rolling_hills.png',
    tag: 'Rockfall',
    confidence: 0.942,
    timestamp: '10 mins ago',
    status: 'pending',
    verificationStatus: 'unverified',
    submissionPersona: 'Local Resident',
    accuracyRadiusMeters: 12,
    isClusterFlagged: true,
    locationName: 'Hunthar Veng Junction (NH-6)',
    reporterPhone: '+91 98625 11234',
    description: 'Boulders blocked primary lane near Hunthar Veng junction. Water pooling fast across hillside.',
    multiPhotos: ['/bg_rolling_hills.png'],
    operatorLog: 'Ingested via Citizen Hazard Portal at 10:08 IST'
  },
  {
    id: 'INC-2026-SL088',
    lat: 23.7390,
    lng: 92.7095,
    photoUrl: '/bg_rolling_hills.png',
    tag: 'Rockfall',
    confidence: 0.915,
    timestamp: '14 mins ago',
    status: 'pending',
    verificationStatus: 'unverified',
    submissionPersona: 'Tourist / Traveler',
    accuracyRadiusMeters: 25,
    isClusterFlagged: true,
    locationName: 'Hunthar Hill Slope Sector B',
    reporterPhone: '+91 94361 77110',
    description: 'Multiple small rockslips falling onto highway near Hunthar curve. Cars stopping.',
    multiPhotos: ['/bg_rolling_hills.png'],
    operatorLog: 'Ingested via Mobile Emergency SOS at 10:04 IST'
  },
  {
    id: 'INC-2026-SL082',
    lat: 23.7150,
    lng: 92.7310,
    photoUrl: '/bg_rolling_hills.png',
    tag: 'Mudslide',
    confidence: 0.964,
    timestamp: '25 mins ago',
    status: 'approved',
    verificationStatus: 'verified_onsite',
    submissionPersona: 'Local Resident',
    accuracyRadiusMeters: 8,
    isClusterFlagged: false,
    locationName: 'Sonapur Ridge Corridor',
    reporterPhone: '+91 94361 88219',
    description: 'Heavy wet soil slip across Sonapur Ridge. Heavy trucks slipping.',
    operatorLog: 'Verified On-Site by Operator ID #409 at 09:55 IST'
  },
  {
    id: 'INC-2026-SL079',
    lat: 23.7210,
    lng: 92.7210,
    photoUrl: '/bg_rolling_hills.png',
    tag: 'Road Crack',
    confidence: 0.880,
    timestamp: '42 mins ago',
    status: 'pending',
    verificationStatus: 'unverified',
    submissionPersona: 'Tourist / Traveler',
    accuracyRadiusMeters: 18,
    isClusterFlagged: false,
    locationName: 'Kolasib Bypass Milepost 12',
    reporterPhone: '+91 98620 33491',
    description: 'Deep transverse tarmac crack opening up on the outer lane.',
    operatorLog: 'Ingested via Tourist Safety App at 09:36 IST'
  }
];

// Leaflet DivIcon for report location marker
const createGeotagMarker = (color: string) => {
  return L.divIcon({
    className: 'custom-geotag-marker',
    html: `
      <div style="position: relative; display: flex; align-items: center; justify-content: center;">
        <div style="position: absolute; width: 34px; height: 34px; border-radius: 50%; background-color: ${color}; opacity: 0.35; animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
        <div style="width: 26px; height: 26px; border-radius: 50%; background-color: ${color}; border: 2.5px solid #ffffff; box-shadow: 0 0 16px ${color}; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; color: white;">
          📍
        </div>
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  });
};

export const IncidentModerationWorkspace: React.FC<IncidentModerationWorkspaceProps> = ({ 
  onBackToDashboard,
  onApproveIncident
}) => {
  const [incidents, setIncidents] = useState<CitizenIncident[]>(initialModerationIncidents);
  const [selectedId, setSelectedId] = useState<string | null>('INC-2026-SL087');
  const [activeFilter, setActiveFilter] = useState<'all' | 'unverified' | 'cluster'>('all');
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Fetch live reports from backend and merge with seed data
  const fetchLiveReports = useCallback(async () => {
    try {
      const reports = await listReports(50);
      if (reports.length > 0) {
        const liveIncidents: CitizenIncident[] = reports.map((r) => ({
          id: String(r.id),
          lat: r.latitude,
          lng: r.longitude,
          photoUrl: '/bg_rolling_hills.png',
          tag: r.ai_classification as CitizenIncident['tag'],
          confidence: r.ai_confidence_pct / 100,
          timestamp: new Date(r.submitted_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
          status: r.verified_by_volunteer ? 'approved' : 'pending',
          verificationStatus: r.verified_by_volunteer ? 'verified_onsite' : 'unverified',
          submissionPersona: 'Local Resident',
          operatorLog: `Ingested from backend at ${new Date(r.submitted_at).toLocaleTimeString('en-IN')}`,
        }));
        // Merge: keep mock seeds at the end for demo richness
        setIncidents((prev) => {
          const existingIds = new Set(liveIncidents.map((i) => i.id));
          const seeds = prev.filter((p) => !existingIds.has(p.id) && p.id.startsWith('INC-'));
          return [...liveIncidents, ...seeds];
        });
      }
    } catch {
      // backend unreachable — keep mock data
    }
  }, []);

  useEffect(() => {
    fetchLiveReports();
    const id = setInterval(fetchLiveReports, 20_000);
    return () => clearInterval(id);
  }, [fetchLiveReports]);

  const [isMergeModalOpen, setIsMergeModalOpen] = useState<boolean>(false);
  const [masterTargetId, setMasterTargetId] = useState<string>('INC-2026-SL082');

  const selectedReport = incidents.find(i => i.id === selectedId) || null;

  // Real-time Operational Counters
  const pendingCount = incidents.filter(i => i.verificationStatus === 'unverified' || !i.verificationStatus).length;
  const verifiedCount = incidents.filter(i => i.verificationStatus === 'verified_onsite' || i.verificationStatus === 'approved').length;
  const mergedCount = incidents.filter(i => i.mergedIntoId).length + 3; // Seed count

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Action: Approve & Publish to Map
  const handleApprove = (id: string) => {
    const updated = incidents.map(item => {
      if (item.id === id) {
        return {
          ...item,
          status: 'approved' as const,
          verificationStatus: 'approved' as const,
          operatorLog: `Approved by Operator ID #409 at ${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })} IST`
        };
      }
      return item;
    });
    setIncidents(updated);

    const approvedItem = updated.find(i => i.id === id);
    if (approvedItem && onApproveIncident) {
      onApproveIncident(approvedItem);
    }

    showToast(`Report ${id} approved & published to Command Dashboard Map!`);
  };

  // Action: Flag as False Alarm
  const handleFalseAlarm = (id: string) => {
    setIncidents(incidents.map(item => {
      if (item.id === id) {
        return {
          ...item,
          status: 'rejected' as const,
          verificationStatus: 'false_alarm' as const,
          operatorLog: `Flagged as False Alarm by Operator ID #409 at ${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })} IST`
        };
      }
      return item;
    }));
    showToast(`Report ${id} flagged as False Alarm & archived.`);
  };

  // Action: Tag as Verified On-Site
  const handleVerifiedOnsite = (id: string) => {
    setIncidents(incidents.map(item => {
      if (item.id === id) {
        return {
          ...item,
          verificationStatus: 'verified_onsite' as const,
          operatorLog: `Verified On-Site (Field Responder Approved) by Operator ID #409 at ${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })} IST`
        };
      }
      return item;
    }));
    showToast(`Report ${id} tagged as Verified On-Site by Field Responder.`);
  };

  // Action: Merge into Master Incident
  const handleMergeSubmit = () => {
    if (!selectedReport) return;
    
    setIncidents(incidents.map(item => {
      if (item.id === selectedReport.id) {
        return {
          ...item,
          mergedIntoId: masterTargetId,
          operatorLog: `Merged into Master Incident ${masterTargetId} by Operator ID #409 at ${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })} IST`
        };
      }
      return item;
    }));

    setIsMergeModalOpen(false);
    showToast(`Merged report ${selectedReport.id} into Master Incident ${masterTargetId}.`);
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

      {/* Top Banner & Operational Header */}
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

          <div className="w-10 h-10 rounded-2xl bg-slate-900 text-emerald-400 flex items-center justify-center shadow-lg shrink-0">
            <ShieldCheck className="w-6 h-6 text-[#10b981]" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg sm:text-xl font-black text-slate-900 tracking-tight">
                Incident Moderation Desk
              </h1>
              <span className="bg-emerald-100 text-[#10b981] text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full border border-emerald-300">
                Zone 4 Command Center
              </span>
            </div>
            <p className="text-xs text-slate-600 font-medium">
              Citizen Hazard Report Verification, Spatial De-duplication &amp; Field Moderation
            </p>
          </div>
        </div>

        {/* Operational Real-Time Counters */}
        <div className="flex items-center gap-3">
          
          <div className="bg-white/80 border border-slate-200 px-3.5 py-1.5 rounded-2xl text-center shadow-sm">
            <span className="text-[10px] font-bold text-slate-500 block uppercase">Pending Queue</span>
            <span className="text-base font-black text-amber-600">{pendingCount}</span>
          </div>

          <div className="bg-white/80 border border-slate-200 px-3.5 py-1.5 rounded-2xl text-center shadow-sm">
            <span className="text-[10px] font-bold text-slate-500 block uppercase">Verified Today</span>
            <span className="text-base font-black text-[#10b981]">{verifiedCount}</span>
          </div>

          <div className="bg-white/80 border border-slate-200 px-3.5 py-1.5 rounded-2xl text-center shadow-sm">
            <span className="text-[10px] font-bold text-slate-500 block uppercase">Merged Duplicates</span>
            <span className="text-base font-black text-purple-600">{mergedCount}</span>
          </div>

        </div>
      </div>

      {/* Main 3-Column Split Viewport Layout (30% / 45% / 25%) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* COLUMN 1 (30% / lg:col-span-4): Ingestion Queue List */}
        <div className="lg:col-span-4">
          <ModerationQueuePanel 
            incidents={incidents}
            selectedId={selectedId}
            onSelectIncident={(id) => setSelectedId(id)}
            activeFilter={activeFilter}
            onFilterChange={(f) => setActiveFilter(f)}
          />
        </div>

        {/* COLUMN 2 (45% / lg:col-span-5): Detailed Report Inspector */}
        <div className="lg:col-span-5 glass-panel-light rounded-3xl p-5 flex flex-col justify-between h-[760px] border border-white/80 shadow-xl overflow-y-auto space-y-4">
          {selectedReport ? (
            <div className="space-y-4 flex-1 flex flex-col justify-between">
              
              <div className="space-y-4">
                {/* Inspector Header */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-200">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-base font-black text-slate-900">
                        {selectedReport.id}
                      </span>
                      <span className="bg-slate-900 text-emerald-400 text-xs font-black px-2.5 py-0.5 rounded-md uppercase">
                        {selectedReport.tag}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 font-medium mt-0.5 flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-[#10b981]" />
                      <span>{selectedReport.locationName || 'Unknown Location'}</span>
                    </p>
                  </div>

                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 font-mono block">AI Confidence Score</span>
                    <div className="flex items-center gap-1 mt-0.5">
                      <div className="w-16 h-2 bg-slate-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-[#10b981]" 
                          style={{ width: `${Math.round(selectedReport.confidence * 100)}%` }} 
                        />
                      </div>
                      <span className="text-xs font-black text-slate-800 font-mono">
                        {Math.round(selectedReport.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Photo Evidence & GPS Accuracy Card */}
                <div className="relative rounded-2xl overflow-hidden border border-slate-200/90 shadow-inner group">
                  <img 
                    src={selectedReport.photoUrl} 
                    alt="Citizen Hazard Photo Evidence" 
                    className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent flex items-end justify-between p-3 text-white text-xs">
                    <div className="flex items-center gap-2">
                      <span className="bg-slate-900/90 backdrop-blur-md px-2.5 py-1 rounded-full text-[11px] font-bold border border-white/20">
                        Accuracy Radius: ±{selectedReport.accuracyRadiusMeters || 12}m
                      </span>
                      <span className="bg-[#10b981]/90 backdrop-blur-md px-2.5 py-1 rounded-full text-[11px] font-bold">
                        GPS Verified
                      </span>
                    </div>
                    <button className="bg-white/20 hover:bg-white/40 p-1.5 rounded-full backdrop-blur-md transition-all">
                      <Maximize2 className="w-4 h-4 text-white" />
                    </button>
                  </div>
                </div>

                {/* Submitter Reporter Metadata */}
                <div className="grid grid-cols-2 gap-3 bg-slate-100/90 p-3 rounded-2xl border border-slate-200 text-xs">
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 block uppercase">Submission Persona</span>
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md font-bold mt-1 ${
                      selectedReport.submissionPersona === 'Tourist / Traveler'
                        ? 'bg-amber-100 text-amber-900'
                        : 'bg-emerald-100 text-emerald-900'
                    }`}>
                      {selectedReport.submissionPersona === 'Tourist / Traveler' ? <Compass className="w-3 h-3" /> : <User className="w-3 h-3" />}
                      <span>{selectedReport.submissionPersona || 'Local Resident'}</span>
                    </span>
                  </div>

                  <div>
                    <span className="text-[10px] font-bold text-slate-500 block uppercase">Reporter Contact</span>
                    <div className="flex items-center gap-1.5 font-mono font-bold text-slate-800 mt-1">
                      <Phone className="w-3 h-3 text-[#10b981]" />
                      <span>{selectedReport.reporterPhone || '+91 98625 00000'}</span>
                    </div>
                  </div>
                </div>

                {/* Description Box */}
                <div className="space-y-1">
                  <label className="block text-xs font-bold text-slate-700">Citizen Description</label>
                  <div className="p-3 rounded-2xl bg-white border border-slate-200 text-xs text-slate-800 font-medium leading-relaxed shadow-sm">
                    "{selectedReport.description}"
                  </div>
                </div>

                {/* 500m Spatial Duplicate Alert Banner */}
                {selectedReport.isClusterFlagged && (
                  <div className="bg-amber-50 border-l-4 border-amber-500 p-3.5 rounded-r-2xl text-amber-900 text-xs font-bold flex items-center justify-between shadow-sm animate-in fade-in duration-200">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
                      <div>
                        <span>⚠️ Potential Duplicate: 3 nearby reports found within 500m</span>
                        <p className="text-[10px] text-amber-800 font-normal">
                          Geospatial proximity match with active incident INC-2026-SL082.
                        </p>
                      </div>
                    </div>

                    <button
                      onClick={() => setIsMergeModalOpen(true)}
                      className="bg-purple-600 hover:bg-purple-700 text-white text-[11px] font-bold px-3 py-1.5 rounded-xl shadow transition-all flex items-center gap-1 shrink-0 cursor-pointer"
                    >
                      <GitMerge className="w-3.5 h-3.5" />
                      <span>Merge Incident</span>
                    </button>
                  </div>
                )}

                {/* Verification Pipeline Dropdown */}
                <div className="space-y-1.5">
                  <label className="block text-xs font-bold text-slate-700">Verification Status Pipeline</label>
                  <select
                    value={selectedReport.verificationStatus || 'unverified'}
                    onChange={(e) => {
                      const val = e.target.value as any;
                      if (val === 'approved') handleApprove(selectedReport.id);
                      else if (val === 'false_alarm') handleFalseAlarm(selectedReport.id);
                      else if (val === 'verified_onsite') handleVerifiedOnsite(selectedReport.id);
                    }}
                    className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] focus:ring-2 focus:ring-[#10b981]/20 rounded-xl px-3 py-2 text-xs font-bold text-slate-900"
                  >
                    <option value="unverified">Unverified Citizen Report</option>
                    <option value="verified_onsite">Verified On-Site (Field Responder Approved)</option>
                    <option value="approved">Approved &amp; Published to Map</option>
                    <option value="false_alarm">False Alarm / Cleared</option>
                  </select>
                </div>

              </div>

              {/* Action Controls Bar */}
              <div className="space-y-3 pt-3 border-t border-slate-200">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  
                  {/* Approve & Publish */}
                  <button
                    onClick={() => handleApprove(selectedReport.id)}
                    className="bg-[#10b981] hover:bg-emerald-600 text-white text-xs font-extrabold py-2.5 px-3 rounded-xl shadow-md transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Approve &amp; Publish</span>
                  </button>

                  {/* Tag Verified On-Site */}
                  <button
                    onClick={() => handleVerifiedOnsite(selectedReport.id)}
                    className="bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-300 text-xs font-bold py-2.5 px-3 rounded-xl transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    <FileCheck2 className="w-4 h-4 text-emerald-600" />
                    <span>Verified On-Site</span>
                  </button>

                  {/* Flag False Alarm */}
                  <button
                    onClick={() => handleFalseAlarm(selectedReport.id)}
                    className="bg-white hover:bg-rose-50 text-rose-600 border border-rose-300 text-xs font-bold py-2.5 px-3 rounded-xl transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    <XCircle className="w-4 h-4 text-rose-500" />
                    <span>False Alarm</span>
                  </button>

                </div>

                {/* Automated Log Footer */}
                <div className="p-2.5 rounded-xl bg-slate-100 border border-slate-200 text-[11px] font-mono text-slate-600 flex items-center gap-2">
                  <History className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                  <span className="truncate">{selectedReport.operatorLog || 'Log tracking initialized.'}</span>
                </div>
              </div>

            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 text-center">
              <Info className="w-10 h-10 mb-2 opacity-50" />
              <p className="text-xs font-bold">Select a citizen report from the queue to inspect details.</p>
            </div>
          )}
        </div>

        {/* COLUMN 3 (25% / lg:col-span-3): Spatial Geotag Map */}
        <div className="lg:col-span-3 glass-panel-emerald-glow rounded-3xl p-4 flex flex-col h-[760px] relative overflow-hidden justify-between">
          
          <div className="flex items-center justify-between mb-2 px-1">
            <div className="flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-[#10b981]" />
              <h2 className="text-xs font-bold text-slate-800 tracking-tight">
                Spatial Geotag Verification Map
              </h2>
            </div>
          </div>

          {/* Leaflet Map Viewport */}
          <div className="relative flex-1 w-full rounded-2xl overflow-hidden shadow-inner border border-slate-200 mb-3">
            <MapContainer
              center={selectedReport ? [selectedReport.lat, selectedReport.lng] : [23.7380, 92.7090]}
              zoom={14}
              style={{ height: '100%', width: '100%' }}
              zoomControl={false}
            >
              <TileLayer
                attribution='&copy; OpenStreetMap'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              {selectedReport && (
                <>
                  <Marker 
                    position={[selectedReport.lat, selectedReport.lng]}
                    icon={createGeotagMarker('#10b981')}
                  >
                    <Popup>
                      <div className="p-1 font-sans">
                        <div className="font-bold text-xs">{selectedReport.id}</div>
                        <div className="text-[10px] text-slate-500">{selectedReport.locationName}</div>
                      </div>
                    </Popup>
                  </Marker>

                  {/* 500m Accuracy / Proximity Radius Circle */}
                  <Circle 
                    center={[selectedReport.lat, selectedReport.lng]}
                    radius={500}
                    pathOptions={{
                      color: '#10b981',
                      fillColor: '#10b981',
                      fillOpacity: 0.15,
                      dashArray: '5, 5'
                    }}
                  />
                </>
              )}
            </MapContainer>

            {/* Top-Right Floating Coordinates Pill */}
            {selectedReport && (
              <div className="absolute top-3 right-3 z-[1000] bg-white/90 backdrop-blur-md px-2.5 py-1 rounded-full shadow-md text-[10px] font-mono font-bold text-slate-800 border border-slate-200">
                {selectedReport.lat.toFixed(4)}° N, {selectedReport.lng.toFixed(4)}° E
              </div>
            )}
          </div>

          {/* Geotag Metrics Card */}
          {selectedReport && (
            <div className="p-3 rounded-2xl bg-white/80 border border-slate-200 text-xs space-y-2">
              <div className="flex justify-between items-center font-bold text-slate-700">
                <span>Elevation Estimate</span>
                <span className="font-mono text-emerald-700">1,120m ASL</span>
              </div>
              <div className="flex justify-between items-center font-bold text-slate-700">
                <span>Proximity Hazard Radius</span>
                <span className="font-mono text-slate-900">500m Circle</span>
              </div>
            </div>
          )}

        </div>

      </div>

      {/* MERGE INTO MASTER INCIDENT MODAL DIALOG */}
      {isMergeModalOpen && selectedReport && (
        <div className="fixed inset-0 z-[1200] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 max-w-lg w-full shadow-2xl border border-slate-200 animate-in zoom-in-95 duration-150 space-y-4">
            
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center gap-2">
                <GitMerge className="w-5 h-5 text-purple-600" />
                <h3 className="text-sm font-extrabold text-slate-900">
                  Merge into Master Incident
                </h3>
              </div>
              <button 
                onClick={() => setIsMergeModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 p-1 rounded-full"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-600 font-medium">
              Combine report <strong className="text-slate-900 font-mono">{selectedReport.id}</strong> into an existing active incident within 500m proximity. Photos and descriptions will be consolidated into a multi-photo activity stream.
            </p>

            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-slate-700">Select Target Master Incident ID</label>
              <select
                value={masterTargetId}
                onChange={(e) => setMasterTargetId(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 rounded-xl px-3 py-2 text-xs font-bold text-slate-900"
              >
                <option value="INC-2026-SL082">INC-2026-SL082 (Sonapur Ridge Landslide)</option>
                <option value="INC-2026-SL079">INC-2026-SL079 (Kolasib Transverse Crack)</option>
                <option value="INC-2026-SL087">INC-2026-SL087 (Hunthar Veng Rockfall)</option>
              </select>
            </div>

            <div className="p-3 rounded-2xl bg-purple-50 border border-purple-200 text-xs text-purple-900 font-semibold space-y-1">
              <div className="font-bold flex items-center gap-1.5">
                <Check className="w-4 h-4 text-purple-600" />
                <span>Consolidated Stream Preview:</span>
              </div>
              <p className="text-[11px] text-purple-800 font-normal">
                "{selectedReport.description}" will be appended to {masterTargetId} stream with 2 photos.
              </p>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <button
                onClick={() => setIsMergeModalOpen(false)}
                className="w-1/2 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-100 transition-all cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleMergeSubmit}
                className="w-1/2 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-extrabold text-xs shadow-md transition-all cursor-pointer"
              >
                Confirm &amp; Merge Report
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
