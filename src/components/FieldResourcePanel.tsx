import React, { useState } from 'react';
import { 
  PackageCheck, 
  Radio, 
  Wifi, 
  AlertTriangle, 
  Navigation
} from 'lucide-react';
import type { FieldResourceState } from '../types/dashboard';

interface FieldResourcePanelProps {
  resourceState: FieldResourceState;
  onUpdateSupplies: (
    medical: FieldResourceState['medicalSupplies'], 
    rations: FieldResourceState['rations'], 
    sat: FieldResourceState['satellitePhone']
  ) => void;
  onPingGPS: (coords: [number, number]) => void;
}

export const FieldResourcePanel: React.FC<FieldResourcePanelProps> = ({
  resourceState,
  onUpdateSupplies,
  onPingGPS
}) => {
  const [medical, setMedical] = useState<FieldResourceState['medicalSupplies']>(resourceState.medicalSupplies);
  const [rations, setRations] = useState<FieldResourceState['rations']>(resourceState.rations);
  const [satPhone, setSatPhone] = useState<FieldResourceState['satellitePhone']>(resourceState.satellitePhone);
  const [isPinging, setIsPinging] = useState<boolean>(false);
  const [lastPingTime, setLastPingTime] = useState<string | null>('10:24 IST');

  const handleMedicalChange = (val: FieldResourceState['medicalSupplies']) => {
    setMedical(val);
    onUpdateSupplies(val, rations, satPhone);
  };

  const handleRationsChange = (val: FieldResourceState['rations']) => {
    setRations(val);
    onUpdateSupplies(medical, val, satPhone);
  };

  const handleSatPhoneChange = (val: FieldResourceState['satellitePhone']) => {
    setSatPhone(val);
    onUpdateSupplies(medical, rations, val);
  };

  const handleGPSPingClick = () => {
    setIsPinging(true);
    
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude;
          const lng = pos.coords.longitude;
          onPingGPS([lat, lng]);
          setIsPinging(false);
          setLastPingTime(new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) + ' IST');
        },
        () => {
          // Fallback location near Hunthar Veng
          onPingGPS([23.7380, 92.7090]);
          setIsPinging(false);
          setLastPingTime(new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) + ' IST');
        }
      );
    } else {
      onPingGPS([23.7380, 92.7090]);
      setIsPinging(false);
      setLastPingTime(new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) + ' IST');
    }
  };

  return (
    <div className="glass-panel-light rounded-3xl p-5 border border-white/90 shadow-xl flex flex-col justify-between gap-4 h-full overflow-y-auto font-sans">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-slate-900 text-emerald-400 flex items-center justify-center font-bold">
            <PackageCheck className="w-4 h-4 text-[#10b981]" />
          </div>
          <div>
            <h3 className="text-sm font-black text-slate-900 tracking-tight">
              Emergency Supplies &amp; GPS Transceiver
            </h3>
            <p className="text-[10px] text-slate-500 font-mono">
              Field Logistics &amp; Location Beacon
            </p>
          </div>
        </div>

        <span className="bg-emerald-100 text-[#10b981] border border-emerald-300 font-mono text-[10px] font-bold px-2.5 py-1 rounded-full flex items-center gap-1">
          <Radio className="w-3 h-3 text-[#10b981] animate-pulse" />
          <span>Beacon Active</span>
        </span>
      </div>

      {/* Field Supply Selectors */}
      <div className="space-y-4">
        
        {/* Medical Stock */}
        <div className="space-y-1.5 p-3 rounded-2xl bg-white/70 border border-slate-200 shadow-sm">
          <div className="flex justify-between items-center text-xs font-bold text-slate-800">
            <span>Medical Kits &amp; Trauma Trauma Supplies</span>
            <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full ${
              medical === 'Sufficient' ? 'bg-emerald-100 text-emerald-900' : medical === 'Low' ? 'bg-amber-100 text-amber-900' : 'bg-rose-100 text-rose-900'
            }`}>
              {medical}
            </span>
          </div>

          <div className="grid grid-cols-3 gap-1.5 pt-1">
            <button
              onClick={() => handleMedicalChange('Sufficient')}
              className={`py-1.5 px-2 rounded-xl text-[11px] font-bold transition-all cursor-pointer ${
                medical === 'Sufficient' ? 'bg-emerald-600 text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Sufficient
            </button>
            <button
              onClick={() => handleMedicalChange('Low')}
              className={`py-1.5 px-2 rounded-xl text-[11px] font-bold transition-all cursor-pointer ${
                medical === 'Low' ? 'bg-amber-500 text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Low
            </button>
            <button
              onClick={() => handleMedicalChange('Critical')}
              className={`py-1.5 px-2 rounded-xl text-[11px] font-bold transition-all cursor-pointer ${
                medical === 'Critical' ? 'bg-rose-600 text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Critical
            </button>
          </div>
        </div>

        {/* Emergency Rations */}
        <div className="space-y-1.5 p-3 rounded-2xl bg-white/70 border border-slate-200 shadow-sm">
          <div className="flex justify-between items-center text-xs font-bold text-slate-800">
            <span>High-Energy Rations &amp; Clean Water</span>
            <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full ${
              rations === 'Sufficient' ? 'bg-emerald-100 text-emerald-900' : 'bg-amber-100 text-amber-900'
            }`}>
              {rations}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-1.5 pt-1">
            <button
              onClick={() => handleRationsChange('Sufficient')}
              className={`py-1.5 px-2 rounded-xl text-[11px] font-bold transition-all cursor-pointer ${
                rations === 'Sufficient' ? 'bg-emerald-600 text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Sufficient
            </button>
            <button
              onClick={() => handleRationsChange('Low')}
              className={`py-1.5 px-2 rounded-xl text-[11px] font-bold transition-all cursor-pointer ${
                rations === 'Low' ? 'bg-amber-500 text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Low
            </button>
          </div>
        </div>

        {/* Satellite Phone Signal */}
        <div className="space-y-1.5 p-3 rounded-2xl bg-white/70 border border-slate-200 shadow-sm">
          <div className="flex justify-between items-center text-xs font-bold text-slate-800">
            <span>Satellite Transceiver Signal</span>
            <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full ${
              satPhone === 'Active' ? 'bg-emerald-100 text-emerald-900' : 'bg-amber-100 text-amber-900'
            }`}>
              {satPhone}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-1.5 pt-1">
            <button
              onClick={() => handleSatPhoneChange('Active')}
              className={`py-1.5 px-2 rounded-xl text-[11px] font-bold transition-all cursor-pointer flex items-center justify-center gap-1 ${
                satPhone === 'Active' ? 'bg-[#10b981] text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              <Wifi className="w-3 h-3" />
              <span>Active Signal</span>
            </button>
            <button
              onClick={() => handleSatPhoneChange('Weak')}
              className={`py-1.5 px-2 rounded-xl text-[11px] font-bold transition-all cursor-pointer flex items-center justify-center gap-1 ${
                satPhone === 'Weak' ? 'bg-amber-500 text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              <AlertTriangle className="w-3 h-3" />
              <span>Weak Signal</span>
            </button>
          </div>
        </div>

      </div>

      {/* Field Geolocation Transceiver Action Button */}
      <div className="space-y-2 pt-2 border-t border-slate-200">
        <button
          onClick={handleGPSPingClick}
          disabled={isPinging}
          className="w-full py-3.5 rounded-2xl bg-[#10b981] hover:bg-emerald-600 disabled:opacity-50 text-white font-extrabold text-xs shadow-lg shadow-emerald-500/25 transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95"
        >
          <Navigation className={`w-4 h-4 ${isPinging ? 'animate-spin' : ''}`} />
          <span>Transmit Field Unit Location (GPS Ping)</span>
        </button>

        {lastPingTime && (
          <div className="text-[10px] font-mono text-center text-slate-500">
            Last Transmit Ping: <strong>{lastPingTime}</strong> • Refreshes Responder Marker on Map
          </div>
        )}
      </div>

    </div>
  );
};
