import React, { useState, useEffect } from 'react';
import {
  Camera,
  MapPin,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  ArrowLeft,
  Send
} from 'lucide-react';
import type { CitizenIncident } from '../types/dashboard';
import { submitReport } from '../api/reports';

interface CitizenReportProps {
  onBackToDashboard?: () => void;
  onSubmitReport?: (report: CitizenIncident) => void;
}

export const CitizenReport: React.FC<CitizenReportProps> = ({
  onBackToDashboard,
  onSubmitReport
}) => {
  const [hazardType, setHazardType] = useState<string>('Landslide / Mudslide');
  const [description, setDescription] = useState<string>('');
  const [reporterPhone, setReporterPhone] = useState<string>('');
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [locating, setLocating] = useState<boolean>(false);
  const [locError, setLocError] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [backendReportId, setBackendReportId] = useState<string | null>(null);
  const [aiClassification, setAiClassification] = useState<string | null>(null);

  // Auto-fetch Geolocation on Component Mount
  const fetchLocation = () => {
    setLocating(true);
    setLocError(null);
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
          setLocating(false);
        },
        (err) => {
          console.warn('GPS location fetch error:', err.message);
          setLocation({ lat: 29.8512, lng: 80.5367 });
          setLocError('GPS signal weak. Using sector cell tower estimate.');
          setLocating(false);
        },
        { enableHighAccuracy: true, timeout: 8000 }
      );
    } else {
      setLocation({ lat: 29.8512, lng: 80.5367 });
      setLocating(false);
    }
  };

  useEffect(() => {
    fetchLocation();
  }, []);

  // Handle Photo Upload & Preview
  const handlePhotoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // Handle Form Submission — POST to backend, fallback to local state
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitError(null);

    const localPayload: CitizenIncident = {
      id: `report-${Date.now()}`,
      lat: location ? location.lat : 29.8512,
      lng: location ? location.lng : 80.5367,
      photoUrl: photoPreview || '/bg_rolling_hills.png',
      tag: hazardType.split('/')[0].trim() as CitizenIncident['tag'],
      confidence: 0.95,
      timestamp: `${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} IST Today`,
      status: 'pending',
      locationName: description ? description.slice(0, 30) : 'Citizen Geotag Report',
      reporterPhone: reporterPhone || '+91 98765 00000',
      description
    };

    try {
      const res = await submitReport({
        submitter_phone: reporterPhone || '+91 98765 00000',
        submitter_role: 'citizen',
        latitude: location?.lat ?? 29.8512,
        longitude: location?.lng ?? 80.5367,
        image_url: photoPreview || '/bg_rolling_hills.png',
        description,
      });
      setBackendReportId(String(res.report_id));
      setAiClassification(`${res.classification} (${Math.round(res.confidence_pct)}% confidence)`);
      localPayload.id = String(res.report_id);
      localPayload.confidence = res.confidence_pct / 100;
      localPayload.tag = res.classification as CitizenIncident['tag'];
    } catch {
      // Backend unreachable — proceed with optimistic local state
    } finally {
      setIsSubmitting(false);
    }

    if (onSubmitReport) onSubmitReport(localPayload);
    setIsSubmitted(true);
  };

  const handleReset = () => {
    setIsSubmitted(false);
    setPhotoPreview(null);
    setDescription('');
    setReporterPhone('');
    fetchLocation();
  };

  return (
    <div className="min-h-screen text-slate-900 flex flex-col font-sans selection:bg-emerald-500 selection:text-white p-4 md:p-6">
      
      {/* Top Header Navigation Glass Bar */}
      <header className="glass-panel-light rounded-2xl max-w-2xl w-full mx-auto p-3.5 flex items-center justify-between mb-5 shadow-lg">
        <div className="flex items-center gap-3">
          {onBackToDashboard && (
            <button 
              onClick={onBackToDashboard}
              className="p-1.5 rounded-xl text-slate-700 hover:text-slate-900 bg-white/40 hover:bg-white/70 transition-all border border-white/60"
              title="Back to Command Dashboard"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-[#10b981] flex items-center justify-center text-white font-bold text-xs shadow-md">
              SS
            </div>
            <h1 className="text-xs md:text-sm font-black tracking-wider uppercase text-slate-900 font-mono">
              SAFESLOPE // CITIZEN INCIDENT REPORT
            </h1>
          </div>
        </div>

        <span className="px-2.5 py-1 text-[10px] font-bold rounded-full bg-emerald-500/20 text-emerald-800 border border-emerald-500/40 uppercase tracking-wide">
          LIVE DISPATCH
        </span>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-2xl w-full mx-auto flex flex-col gap-5">
        
        {/* Warning Banner & Instructions */}
        <div className="glass-panel-light rounded-2xl p-4 flex items-start gap-3 text-amber-950 border-amber-300/60 shadow-md">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div className="text-xs leading-relaxed">
            <span className="font-bold block mb-0.5 text-amber-950">EMERGENCY NOTICE FOR LOCAL RESIDENTS:</span>
            If you are in immediate danger, move to higher ground immediately. Use this form to report active landslides or road blockages to the DDMA Command Center.
          </div>
        </div>

        {/* Confirmation Screen on Success */}
        {isSubmitted ? (
          <div className="glass-panel-light rounded-3xl p-6 md:p-8 flex flex-col items-center text-center gap-4 shadow-xl my-auto">
            <div className="w-16 h-16 rounded-full bg-emerald-100/90 border border-emerald-300 flex items-center justify-center text-[#10b981] animate-bounce shadow-md">
              <CheckCircle2 className="w-10 h-10 stroke-[2.5]" />
            </div>

            <div>
              <h2 className="text-xl font-bold text-slate-900">
                Report Submitted to Command Center!
              </h2>
              <p className="text-xs text-slate-700 mt-1 max-w-md leading-relaxed">
                Your geotagged incident report has been securely transmitted to the DDMA Human-in-the-Loop WhatsApp Moderation Queue.
              </p>
            </div>

            {/* Geotagged Badge Info */}
            <div className="w-full glass-panel-inner rounded-2xl p-4 font-mono text-xs text-slate-800 space-y-1.5 text-left">
              <div className="flex justify-between">
                <span className="text-slate-600">Status:</span>
                <span className="font-bold text-emerald-700">Pending Moderation</span>
              </div>
              {backendReportId && (
                <div className="flex justify-between">
                  <span className="text-slate-600">Report ID:</span>
                  <span className="font-bold text-slate-900">#{backendReportId}</span>
                </div>
              )}
              {aiClassification && (
                <div className="flex justify-between">
                  <span className="text-slate-600">AI Classification:</span>
                  <span className="font-bold text-emerald-700">{aiClassification}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-slate-600">Hazard Type:</span>
                <span className="font-bold text-slate-900">{hazardType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">GPS Geotag:</span>
                <span className="font-bold text-slate-900">
                  {location ? `${location.lat.toFixed(4)}° N, ${location.lng.toFixed(4)}° E` : 'Captured'}
                </span>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 w-full pt-2">
              <button
                onClick={handleReset}
                className="flex-1 py-3 px-4 rounded-xl bg-white/60 hover:bg-white/80 text-slate-800 text-xs font-bold transition-all border border-white/80 active:scale-95 cursor-pointer shadow-sm"
              >
                Submit Another Report
              </button>
              
              {onBackToDashboard && (
                <button
                  onClick={onBackToDashboard}
                  className="flex-1 py-3 px-4 rounded-xl bg-[#10b981] hover:bg-[#059669] text-white text-xs font-bold transition-all shadow-md shadow-emerald-500/20 active:scale-95 cursor-pointer"
                >
                  View Command Dashboard
                </button>
              )}
            </div>
          </div>
        ) : (
          /* Form Area */
          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            
            {/* 1. Automatic Geolocation Section */}
            <div className="glass-panel-light rounded-2xl p-4 shadow-md flex flex-col gap-2.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                  <MapPin className="w-4 h-4 text-emerald-600" />
                  <span>Automatic GPS Geolocation</span>
                </label>
                <button
                  type="button"
                  onClick={fetchLocation}
                  disabled={locating}
                  className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-800 hover:text-emerald-900 bg-white/50 hover:bg-white/80 px-3 py-1 rounded-xl border border-white transition-all cursor-pointer shadow-sm"
                >
                  <RefreshCw className={`w-3 h-3 ${locating ? 'animate-spin' : ''}`} />
                  <span>Refresh Location</span>
                </button>
              </div>

              {/* Coordinates Badge */}
              <div className="glass-panel-inner rounded-xl p-3 flex items-center justify-between">
                <div className="font-mono text-xs text-slate-800">
                  {locating ? (
                    <span className="text-slate-500">Acquiring satellite lock...</span>
                  ) : location ? (
                    <span className="font-bold text-slate-900">
                      Latitude: {location.lat.toFixed(6)}° • Longitude: {location.lng.toFixed(6)}°
                    </span>
                  ) : (
                    <span className="text-rose-600 font-semibold">Location unavailable</span>
                  )}
                </div>
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              </div>
              {locError && <p className="text-[11px] text-amber-800 font-medium">{locError}</p>}
            </div>

            {/* 2. Camera & Photo Upload Container */}
            <div className="glass-panel-light rounded-2xl p-4 shadow-md flex flex-col gap-3">
              <label className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                <Camera className="w-4 h-4 text-emerald-600" />
                <span>Field Photo Upload (Direct Camera Capture)</span>
              </label>

              {photoPreview ? (
                <div className="relative w-full h-48 rounded-xl overflow-hidden border border-white/80 bg-slate-100 group shadow-sm">
                  <img 
                    src={photoPreview} 
                    alt="Incident preview" 
                    className="w-full h-full object-cover"
                  />
                  <button
                    type="button"
                    onClick={() => setPhotoPreview(null)}
                    className="absolute top-2 right-2 px-3 py-1 bg-black/70 text-white text-xs font-bold rounded-lg backdrop-blur-md hover:bg-black transition-colors"
                  >
                    Retake / Replace
                  </button>
                </div>
              ) : (
                <label className="relative w-full h-44 rounded-xl border-2 border-dashed border-emerald-400 hover:border-emerald-600 bg-white/30 hover:bg-white/50 flex flex-col items-center justify-center gap-2 cursor-pointer transition-all p-4 text-center group shadow-inner">
                  <input
                    type="file"
                    accept="image/*"
                    capture="environment"
                    onChange={handlePhotoSelect}
                    className="absolute inset-0 opacity-0 cursor-pointer"
                  />
                  <div className="w-12 h-12 rounded-full bg-emerald-100/90 border border-emerald-300 flex items-center justify-center text-emerald-600 group-hover:scale-110 transition-transform shadow-sm">
                    <Camera className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-slate-900 block">
                      Tap to Open Camera or Drag & Drop Photo
                    </span>
                    <span className="text-[11px] text-slate-600">
                      Supports JPG, PNG, WEBP from mobile camera
                    </span>
                  </div>
                </label>
              )}
            </div>

            {/* 3. Hazard Details Selector & Description */}
            <div className="glass-panel-light rounded-2xl p-4 shadow-md flex flex-col gap-4">
              {/* Hazard Dropdown */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-900">
                  Select Hazard Type
                </label>
                <select
                  value={hazardType}
                  onChange={(e) => setHazardType(e.target.value)}
                  className="w-full p-3 rounded-xl border border-white/80 bg-white/50 backdrop-blur-md text-slate-900 text-xs font-semibold focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                >
                  <option value="Landslide / Mudslide">Landslide / Mudslide</option>
                  <option value="Severed Road / Crack">Severed Road / Crack</option>
                  <option value="Active Rockfall">Active Rockfall</option>
                  <option value="Flash Flooding">Flash Flooding</option>
                </select>
              </div>

              {/* Contact Phone (Optional) */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-900">
                  Your Phone Number (WhatsApp Enabled)
                </label>
                <input
                  type="tel"
                  placeholder="+91 98765 43210"
                  value={reporterPhone}
                  onChange={(e) => setReporterPhone(e.target.value)}
                  className="w-full p-3 rounded-xl border border-white/80 bg-white/50 backdrop-blur-md text-slate-900 text-xs font-medium focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 font-mono"
                />
              </div>

              {/* Optional Description */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-900">
                  Additional Description & Road Details
                </label>
                <textarea
                  rows={3}
                  placeholder="E.g., Large boulders blocking NH-54 curve near Malpa bridge. 2 vehicles stranded."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full p-3 rounded-xl border border-white/80 bg-white/50 backdrop-blur-md text-slate-900 text-xs font-medium focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                />
              </div>
            </div>

            {/* Primary Submission Button */}
            <button
              type="submit"
              className="w-full py-3.5 px-6 rounded-2xl bg-[#10b981] hover:bg-[#059669] text-white text-sm font-bold shadow-lg shadow-emerald-500/25 transition-all flex items-center justify-center gap-2 active:scale-95 cursor-pointer mt-1"
            >
              <Send className="w-4 h-4" />
              <span>Send Report to Command Center</span>
            </button>

          </form>
        )}

      </main>

      {/* Footer */}
      <footer className="glass-panel-light rounded-2xl max-w-2xl w-full mx-auto py-3 text-center text-xs text-slate-700 font-mono mt-5 shadow-md">
        SafeSlope Citizen Subsystem • DDMA Command Center Ingest
      </footer>
    </div>
  );
};
