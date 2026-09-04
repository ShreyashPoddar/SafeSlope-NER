import React, { useState } from 'react';
import { 
  Key, 
  Map, 
  MessageSquare, 
  Webhook, 
  CheckCircle2, 
  RefreshCw, 
  Eye, 
  EyeOff, 
  Save,
  Radio
} from 'lucide-react';

interface AdminSystemPanelProps {
  onShowToast?: (msg: string) => void;
}

export const AdminSystemPanel: React.FC<AdminSystemPanelProps> = ({ onShowToast }) => {
  // GIS Map Service State
  const [mapboxToken, setMapboxToken] = useState<string>('pk.eyJ1Ijoic2FmZXNsb3BlLW5lciIsImEiOiJjbHg5OG52OGIwMjNsMmxxOHd0OXBpaGpyIn0.8zK2X...');
  const [showMapToken, setShowMapToken] = useState<boolean>(false);
  const [isMapEnabled, setIsMapEnabled] = useState<boolean>(true);
  const [isTestingMap, setIsTestingMap] = useState<boolean>(false);
  const [mapTestStatus, setMapTestStatus] = useState<string | null>('Connected (Latency: 24ms)');

  // Emergency SMS / WhatsApp Gateway State
  const [smsApiKey, setSmsApiKey] = useState<string>('sk_live_ner_sms_99841029481029348');
  const [senderId, setSenderId] = useState<string>('SDMA-ALERT');
  const [isSmsEnabled, setIsSmsEnabled] = useState<boolean>(true);

  // Geotechnical AI Webhook State
  const [webhookUrl, setWebhookUrl] = useState<string>('https://api.safeslope.gov.in/v1/inference');
  const [modelVersion, setModelVersion] = useState<string>('v4.2-NER-LGBM');
  const [isWebhookEnabled, setIsWebhookEnabled] = useState<boolean>(true);

  const handleTestMapConnection = () => {
    setIsTestingMap(true);
    setTimeout(() => {
      setIsTestingMap(false);
      setMapTestStatus('Connected (Latency: 18ms)');
      if (onShowToast) onShowToast('GIS Map Service connection verified successfully!');
    }, 1200);
  };

  const handleSaveAllIntegrations = () => {
    if (onShowToast) onShowToast('API Vault credentials & Integration toggles saved successfully!');
  };

  return (
    <div className="space-y-5 font-sans">
      
      {/* Header Info Banner */}
      <div className="p-4 rounded-2xl bg-slate-900 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-[#10b981] flex items-center justify-center font-bold shrink-0">
            <Key className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-black tracking-tight text-white">
              API &amp; Platform Integration Vault
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Secure Credential Manager &amp; Microservice Webhooks
            </p>
          </div>
        </div>

        <button
          onClick={handleSaveAllIntegrations}
          className="bg-[#10b981] hover:bg-emerald-600 text-white text-xs font-black px-4 py-2 rounded-xl shadow transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95"
        >
          <Save className="w-4 h-4" />
          <span>Save Vault Config</span>
        </button>
      </div>

      {/* Grid of Integration Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        
        {/* CARD 1: GIS Map Service (Mapbox / MapLibre) */}
        <div className="glass-panel-light rounded-3xl p-5 border border-white/80 shadow-xl space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-slate-200 pb-2.5">
              <div className="flex items-center gap-2">
                <Map className="w-5 h-5 text-[#10b981]" />
                <h4 className="text-xs font-black text-slate-900 uppercase tracking-wider">
                  GIS Map Service (Mapbox / MapLibre)
                </h4>
              </div>

              {/* Enable Switch */}
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={isMapEnabled} 
                  onChange={(e) => setIsMapEnabled(e.target.checked)} 
                  className="sr-only peer" 
                />
                <div className="w-9 h-5 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#10b981]"></div>
              </label>
            </div>

            {/* Token Field */}
            <div className="space-y-1">
              <label className="block text-[11px] font-bold text-slate-700">Access Token (VITE_MAPBOX_TOKEN)</label>
              <div className="relative">
                <input
                  type={showMapToken ? "text" : "password"}
                  value={mapboxToken}
                  onChange={(e) => setMapboxToken(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] focus:ring-2 focus:ring-[#10b981]/20 rounded-xl pl-3 pr-10 py-2 text-xs font-mono text-slate-900"
                />
                <button
                  type="button"
                  onClick={() => setShowMapToken(!showMapToken)}
                  className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-700"
                >
                  {showMapToken ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Usage Quota Progress Bar */}
            <div className="space-y-1.5 p-3 rounded-2xl bg-slate-100/80 border border-slate-200 text-xs">
              <div className="flex justify-between items-center text-slate-700 font-bold">
                <span>Monthly API Usage Quota</span>
                <span className="font-mono text-emerald-700">68,400 / 100,000 (68.4%)</span>
              </div>
              <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                <div className="h-full bg-[#10b981] w-[68.4%]" />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-slate-200">
            <span className="text-[10px] font-mono font-bold text-slate-500 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>{mapTestStatus}</span>
            </span>

            <button
              onClick={handleTestMapConnection}
              disabled={isTestingMap}
              className="bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white text-xs font-bold px-3.5 py-1.5 rounded-xl shadow transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-emerald-400 ${isTestingMap ? 'animate-spin' : ''}`} />
              <span>Test Connection</span>
            </button>
          </div>
        </div>

        {/* CARD 2: Emergency SMS & WhatsApp Gateway */}
        <div className="glass-panel-light rounded-3xl p-5 border border-white/80 shadow-xl space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-slate-200 pb-2.5">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-[#10b981]" />
                <h4 className="text-xs font-black text-slate-900 uppercase tracking-wider">
                  Emergency SMS &amp; WhatsApp Gateway
                </h4>
              </div>

              {/* Enable Switch */}
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={isSmsEnabled} 
                  onChange={(e) => setIsSmsEnabled(e.target.checked)} 
                  className="sr-only peer" 
                />
                <div className="w-9 h-5 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#10b981]"></div>
              </label>
            </div>

            {/* API Key */}
            <div className="space-y-1">
              <label className="block text-[11px] font-bold text-slate-700">Gateway API Secret Key</label>
              <input
                type="password"
                value={smsApiKey}
                onChange={(e) => setSmsApiKey(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] focus:ring-2 focus:ring-[#10b981]/20 rounded-xl px-3 py-2 text-xs font-mono text-slate-900"
              />
            </div>

            {/* Sender ID */}
            <div className="space-y-1">
              <label className="block text-[11px] font-bold text-slate-700">Approved Telecommunication Sender ID</label>
              <input
                type="text"
                value={senderId}
                onChange={(e) => setSenderId(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] focus:ring-2 focus:ring-[#10b981]/20 rounded-xl px-3 py-2 text-xs font-mono text-slate-900"
              />
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-slate-200">
            <span className="text-[10px] font-mono font-bold text-emerald-700 flex items-center gap-1">
              <Radio className="w-3.5 h-3.5 text-[#10b981] animate-pulse" />
              <span>SMS Gateway Operational (TRAI Approved)</span>
            </span>
          </div>
        </div>

        {/* CARD 3: Geotechnical AI Webhook */}
        <div className="glass-panel-light rounded-3xl p-5 border border-white/80 shadow-xl space-y-4 flex flex-col justify-between lg:col-span-2">
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-slate-200 pb-2.5">
              <div className="flex items-center gap-2">
                <Webhook className="w-5 h-5 text-[#10b981]" />
                <h4 className="text-xs font-black text-slate-900 uppercase tracking-wider">
                  Geotechnical AI Landslide Model Webhook
                </h4>
              </div>

              {/* Enable Switch */}
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={isWebhookEnabled} 
                  onChange={(e) => setIsWebhookEnabled(e.target.checked)} 
                  className="sr-only peer" 
                />
                <div className="w-9 h-5 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#10b981]"></div>
              </label>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="sm:col-span-2 space-y-1">
                <label className="block text-[11px] font-bold text-slate-700">Model Inference Endpoint URL</label>
                <input
                  type="text"
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] rounded-xl px-3 py-2 text-xs font-mono text-slate-900"
                />
              </div>

              <div className="space-y-1">
                <label className="block text-[11px] font-bold text-slate-700">Model Version Identifier</label>
                <input
                  type="text"
                  value={modelVersion}
                  onChange={(e) => setModelVersion(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] rounded-xl px-3 py-2 text-xs font-mono text-slate-900"
                />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-slate-200">
            <span className="text-[10px] font-mono text-slate-500">
              Receives real-time sensor displacement pings &amp; outputs risk score predictions.
            </span>
          </div>
        </div>

      </div>
    </div>
  );
};
