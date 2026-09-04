import React, { useState } from 'react';
import { 
  CloudRain, 
  Radio, 
  Plus, 
  Send, 
  X, 
  AlertTriangle, 
  RefreshCw, 
  Cpu, 
  Check,
  Sliders
} from 'lucide-react';
import type { GeotechSensor } from '../types/dashboard';

interface GeotechControlPanelProps {
  onPublishUpdates?: (weatherOverride: boolean, sensors: GeotechSensor[]) => void;
  onDeploySensor?: (newSensor: GeotechSensor) => void;
}

export const GeotechControlPanel: React.FC<GeotechControlPanelProps> = ({
  onPublishUpdates,
  onDeploySensor
}) => {
  // Manual Weather Override Controls State
  const [isManualOverride, setIsManualOverride] = useState<boolean>(false);
  const [rainfallRate, setRainfallRate] = useState<number>(42.5);
  const [soilMoisture, setSoilMoisture] = useState<number>(65);
  const [groundVibration, setGroundVibration] = useState<number>(0.18);

  // IoT Sensor Hardware State
  const [globalTiltLimit, setGlobalTiltLimit] = useState<number>(2.5);
  const [globalMoistureLimit, setGlobalMoistureLimit] = useState<number>(60);
  const [sensors, setSensors] = useState<GeotechSensor[]>([
    {
      id: 'SENS-101',
      name: 'Piezometer - Hunthar Slope',
      type: 'Piezometer',
      lat: 23.7380,
      lng: 92.7090,
      tiltRateLimit: 2.5,
      moistureLimit: 60,
      status: 'warning'
    },
    {
      id: 'SENS-102',
      name: 'Borehole Tiltmeter - Sonapur Ridge',
      type: 'Tiltmeter',
      lat: 23.7150,
      lng: 92.7310,
      tiltRateLimit: 2.5,
      moistureLimit: 60,
      status: 'active'
    },
    {
      id: 'SENS-103',
      name: 'Pore Pressure Sensor - Kolasib Cut',
      type: 'Pore Pressure Sensor',
      lat: 23.7210,
      lng: 92.7210,
      tiltRateLimit: 3.0,
      moistureLimit: 65,
      status: 'calibrating'
    }
  ]);

  // Modal State for + Deploy New IoT Node
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [newSensorId, setNewSensorId] = useState<string>('SENS-104');
  const [newSensorName, setNewSensorName] = useState<string>('Seismometer Node B');
  const [newSensorType, setNewSensorType] = useState<GeotechSensor['type']>('Seismometer');
  const [newLat, setNewLat] = useState<string>('23.7300');
  const [newLng, setNewLng] = useState<string>('92.7200');

  const handleCreateSensorSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const created: GeotechSensor = {
      id: newSensorId,
      name: newSensorName,
      type: newSensorType,
      lat: parseFloat(newLat) || 23.7271,
      lng: parseFloat(newLng) || 92.7176,
      tiltRateLimit: globalTiltLimit,
      moistureLimit: globalMoistureLimit,
      status: 'active'
    };

    setSensors(prev => [created, ...prev]);
    if (onDeploySensor) {
      onDeploySensor(created);
    }
    setIsModalOpen(false);
  };

  return (
    <div className="glass-panel-light rounded-3xl p-5 md:p-6 border border-white/90 shadow-xl flex flex-col justify-between gap-5 h-full overflow-y-auto">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-slate-900 text-emerald-400 flex items-center justify-center font-bold">
            <Sliders className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-black text-slate-900 tracking-tight">
              Control &amp; Telemetry Calibration
            </h3>
            <p className="text-[10px] text-slate-500 font-mono">
              Geotechnical Domain Specialist Console
            </p>
          </div>
        </div>

        <button
          onClick={() => setIsManualOverride(!isManualOverride)}
          className={`px-3 py-1 rounded-full text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
            isManualOverride 
              ? 'bg-amber-500 text-white shadow-md animate-pulse' 
              : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
          }`}
        >
          <RefreshCw className={`w-3 h-3 ${isManualOverride ? 'animate-spin' : ''}`} />
          <span>{isManualOverride ? 'Manual Active' : 'Auto Feed'}</span>
        </button>
      </div>

      {/* Main Control Cards */}
      <div className="space-y-4">
        
        {/* CARD 1: Meteorological Override & Calibration */}
        <div className="p-4 rounded-2xl bg-white/70 border border-slate-200/80 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CloudRain className="w-4 h-4 text-emerald-600" />
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Meteorological Override &amp; Calibration
              </h4>
            </div>
          </div>

          {/* Prominent Amber Alert Badge when Manual Override Active */}
          {isManualOverride && (
            <div className="bg-amber-50 border-l-4 border-amber-500 p-3 rounded-r-xl text-amber-900 text-xs font-bold flex items-start gap-2 animate-in fade-in duration-200">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <span>⚠️ MANUAL OVERRIDE IN EFFECT</span>
                <p className="text-[10px] font-normal text-amber-800 mt-0.5">
                  Automated telemetry feeds overridden by Specialist input.
                </p>
              </div>
            </div>
          )}

          {/* Numerical Input Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1">
            
            {/* Rainfall Rate Input */}
            <div className="space-y-1">
              <label className="block text-[10px] font-bold text-slate-600">
                Rainfall Rate (mm/h)
              </label>
              <input
                type="number"
                step="0.5"
                value={rainfallRate}
                onChange={(e) => setRainfallRate(parseFloat(e.target.value) || 0)}
                className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] focus:ring-2 focus:ring-[#10b981]/20 rounded-xl px-2.5 py-1.5 text-xs font-bold text-slate-900"
              />
            </div>

            {/* Soil Moisture Input */}
            <div className="space-y-1">
              <label className="block text-[10px] font-bold text-slate-600">
                Soil Saturation (%)
              </label>
              <input
                type="number"
                step="1"
                min="0"
                max="100"
                value={soilMoisture}
                onChange={(e) => setSoilMoisture(parseFloat(e.target.value) || 0)}
                className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] focus:ring-2 focus:ring-[#10b981]/20 rounded-xl px-2.5 py-1.5 text-xs font-bold text-slate-900"
              />
            </div>

            {/* Ground Vibration Index Input */}
            <div className="space-y-1">
              <label className="block text-[10px] font-bold text-slate-600">
                Ground Vibration (g)
              </label>
              <input
                type="number"
                step="0.01"
                value={groundVibration}
                onChange={(e) => setGroundVibration(parseFloat(e.target.value) || 0)}
                className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] focus:ring-2 focus:ring-[#10b981]/20 rounded-xl px-2.5 py-1.5 text-xs font-bold text-slate-900"
              />
            </div>

          </div>
        </div>

        {/* CARD 2: IoT Sensor Node & Trigger Limit Configurator */}
        <div className="p-4 rounded-2xl bg-white/70 border border-slate-200/80 shadow-sm space-y-3">
          
          <div className="flex items-center justify-between border-b border-slate-200 pb-2">
            <div className="flex items-center gap-2">
              <Radio className="w-4 h-4 text-emerald-600" />
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                IoT Sensor Hardware Configurator
              </h4>
            </div>

            <button
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-1 bg-[#10b981] hover:bg-emerald-600 text-white text-[11px] font-bold px-2.5 py-1 rounded-xl shadow transition-all cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Deploy Node</span>
            </button>
          </div>

          {/* Global Threshold Adjusters */}
          <div className="grid grid-cols-2 gap-3 bg-slate-100/80 p-2.5 rounded-xl border border-slate-200">
            <div>
              <label className="block text-[10px] font-bold text-slate-600 mb-1">
                Tilt Rate Limit (mm/h)
              </label>
              <div className="flex items-center gap-1.5">
                <input
                  type="number"
                  step="0.1"
                  value={globalTiltLimit}
                  onChange={(e) => setGlobalTiltLimit(parseFloat(e.target.value) || 2.5)}
                  className="w-full bg-white border border-slate-300 rounded-lg px-2 py-1 text-xs font-bold text-slate-900"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-slate-600 mb-1">
                Moisture Limit (%)
              </label>
              <div className="flex items-center gap-1.5">
                <input
                  type="number"
                  step="1"
                  value={globalMoistureLimit}
                  onChange={(e) => setGlobalMoistureLimit(parseFloat(e.target.value) || 60)}
                  className="w-full bg-white border border-slate-300 rounded-lg px-2 py-1 text-xs font-bold text-slate-900"
                />
              </div>
            </div>
          </div>

          {/* Active Sensor Nodes List */}
          <div className="space-y-2 max-h-[180px] overflow-y-auto pr-1">
            {sensors.map((sns) => (
              <div 
                key={sns.id} 
                className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-200 hover:border-emerald-300 transition-colors text-xs"
              >
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="font-bold text-slate-900">{sns.name}</span>
                    <span className={`text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded ${
                      sns.status === 'warning' ? 'bg-amber-100 text-amber-800' : sns.status === 'active' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-700'
                    }`}>
                      {sns.status}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    ID: {sns.id} • Lat: {sns.lat.toFixed(3)}, Lng: {sns.lng.toFixed(3)}
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-[10px] font-bold text-slate-700">
                    Moisture: {sns.moistureLimit}%
                  </div>
                  <div className="text-[9px] text-slate-400 font-mono mt-0.5">
                    Limit: {sns.tiltRateLimit} mm/h
                  </div>
                </div>
              </div>
            ))}
          </div>

        </div>

      </div>

      {/* Primary Action Button: Publish Updates to Command Dashboard */}
      <button
        onClick={() => {
          if (onPublishUpdates) {
            onPublishUpdates(isManualOverride, sensors);
          }
        }}
        className="w-full py-3 rounded-2xl bg-[#10b981] hover:bg-[#059669] text-white text-xs font-extrabold shadow-lg shadow-emerald-500/25 transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95"
      >
        <Send className="w-4 h-4" />
        <span>Publish Updates to Command Dashboard</span>
      </button>

      {/* MODAL DIALOG: + Deploy New IoT Node */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[1200] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl border border-slate-200 animate-in zoom-in-95 duration-150">
            
            <div className="flex items-center justify-between border-b border-slate-200 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-emerald-600" />
                <h3 className="text-sm font-extrabold text-slate-900">Deploy New IoT Sensor Node</h3>
              </div>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSensorSubmit} className="space-y-3.5">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Sensor Identifier Code</label>
                <input
                  type="text"
                  required
                  value={newSensorId}
                  onChange={(e) => setNewSensorId(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 font-mono text-xs font-bold text-slate-900"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Sensor Location Name</label>
                <input
                  type="text"
                  required
                  value={newSensorName}
                  onChange={(e) => setNewSensorName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-xs font-bold text-slate-900"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Hardware Sensor Type</label>
                <select
                  value={newSensorType}
                  onChange={(e) => setNewSensorType(e.target.value as GeotechSensor['type'])}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-xs font-bold text-slate-900"
                >
                  <option value="Tiltmeter">Tiltmeter (Displacement Rate)</option>
                  <option value="Piezometer">Piezometer (Water Table)</option>
                  <option value="Pore Pressure Sensor">Pore Pressure Sensor</option>
                  <option value="Seismometer">Seismometer (Ground Vib)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Latitude</label>
                  <input
                    type="text"
                    required
                    value={newLat}
                    onChange={(e) => setNewLat(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 font-mono text-xs font-bold text-slate-900"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Longitude</label>
                  <input
                    type="text"
                    required
                    value={newLng}
                    onChange={(e) => setNewLng(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 font-mono text-xs font-bold text-slate-900"
                  />
                </div>
              </div>

              <div className="pt-3 flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="flex-1 py-2.5 rounded-xl border border-slate-300 text-slate-700 text-xs font-bold hover:bg-slate-50 cursor-pointer"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="flex-1 py-2.5 rounded-xl bg-[#10b981] hover:bg-[#059669] text-white text-xs font-bold shadow-md cursor-pointer flex items-center justify-center gap-1.5"
                >
                  <Check className="w-4 h-4" />
                  <span>Deploy Sensor</span>
                </button>
              </div>

            </form>

          </div>
        </div>
      )}

    </div>
  );
};
