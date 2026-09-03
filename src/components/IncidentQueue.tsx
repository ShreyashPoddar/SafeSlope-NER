import React, { useState } from 'react';
import { MoreHorizontal, Sparkles, MessageCircle } from 'lucide-react';
import type { CitizenIncident } from '../types/dashboard';

interface IncidentQueueProps {
  incidents: CitizenIncident[];
  onApproveIncident?: (id: string) => void;
  onRejectIncident?: (id: string) => void;
  onFocusMap?: (lat: number, lng: number) => void;
}

export const IncidentQueue: React.FC<IncidentQueueProps> = ({
  incidents: initialIncidents,
  onApproveIncident,
  onRejectIncident
}) => {
  const [incidents, setIncidents] = useState<CitizenIncident[]>(initialIncidents);

  const handleApprove = (id: string) => {
    setIncidents(prev => prev.map(i => i.id === id ? { ...i, status: 'approved' } : i));
    if (onApproveIncident) onApproveIncident(id);
  };

  const handleReject = (id: string) => {
    setIncidents(prev => prev.map(i => i.id === id ? { ...i, status: 'rejected' } : i));
    if (onRejectIncident) onRejectIncident(id);
  };

  return (
    <div className="glass-panel-light rounded-3xl p-5 flex flex-col h-[390px] justify-between">
      
      {/* Card Header */}
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-base font-bold text-slate-800 tracking-tight">
          Citizen Incident Moderation Queue
        </h2>
        <button className="text-slate-400 hover:text-slate-600 transition-colors p-1">
          <MoreHorizontal className="w-5 h-5" />
        </button>
      </div>

      {/* WhatsApp Incident Feed Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 my-auto">
        
        {/* Card 1: Small Photos Feed Card */}
        <div className="bg-white/40 backdrop-blur-md rounded-2xl p-3 flex flex-col justify-between border border-white/80 shadow-sm hover:border-emerald-300 transition-all">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
                <div className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center text-white shadow-sm">
                  <MessageCircle className="w-3.5 h-3.5 fill-white text-emerald-500" />
                </div>
                <span>WhatsApp</span>
              </div>
              <MoreHorizontal className="w-4 h-4 text-slate-400" />
            </div>

            {/* Photo Thumbnail Grid */}
            <div className="grid grid-cols-2 gap-1.5 rounded-xl overflow-hidden mb-2 h-24 bg-slate-200 shadow-inner">
              <img 
                src="https://images.unsplash.com/photo-1541888946425-d0fbb186a5b3?auto=format&fit=crop&w=600&q=80" 
                alt="Rockfall photo" 
                className="w-full h-full object-cover rounded-l-lg hover:scale-105 transition-transform"
              />
              <img 
                src="https://images.unsplash.com/photo-1517649763962-0c623266010b?auto=format&fit=crop&w=600&q=80" 
                alt="Road damage" 
                className="w-full h-full object-cover rounded-r-lg hover:scale-105 transition-transform"
              />
            </div>

            <div className="text-xs font-bold text-slate-900">Small Photos</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Preceit photo: confirmed</div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-2 mt-3">
            <button
              onClick={() => handleApprove(incidents[0]?.id || 'inc-1')}
              className="py-1.5 px-3 rounded-xl bg-[#10b981] hover:bg-[#059669] text-white text-xs font-semibold shadow-sm transition-all text-center active:scale-95 cursor-pointer"
            >
              Approve
            </button>
            <button
              onClick={() => handleReject(incidents[0]?.id || 'inc-1')}
              className="py-1.5 px-3 rounded-xl bg-slate-200/80 hover:bg-slate-300 text-slate-700 text-xs font-semibold border border-slate-300/80 transition-all text-center active:scale-95 cursor-pointer"
            >
              Reject
            </button>
          </div>
        </div>

        {/* Card 2: AI Labels - Photos Integrated */}
        <div className="bg-white/40 backdrop-blur-md rounded-2xl p-3 flex flex-col justify-between border border-white/80 shadow-sm hover:border-emerald-300 transition-all">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
                <div className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center text-white shadow-sm">
                  <MessageCircle className="w-3.5 h-3.5 fill-white text-emerald-500" />
                </div>
                <span>WhatsApp</span>
              </div>
              <MoreHorizontal className="w-4 h-4 text-slate-400" />
            </div>

            {/* Photo Thumbnail Grid */}
            <div className="grid grid-cols-2 gap-1.5 rounded-xl overflow-hidden mb-2 h-24 bg-slate-200 shadow-inner">
              <img 
                src="https://images.unsplash.com/photo-1508873696983-2df5057c0256?auto=format&fit=crop&w=600&q=80" 
                alt="Mudslide photo" 
                className="w-full h-full object-cover rounded-l-lg hover:scale-105 transition-transform"
              />
              <div className="relative w-full h-full bg-slate-800 flex items-center justify-center overflow-hidden rounded-r-lg">
                <img 
                  src="https://images.unsplash.com/photo-1517649763962-0c623266010b?auto=format&fit=crop&w=600&q=80" 
                  alt="Road detail" 
                  className="w-full h-full object-cover opacity-80"
                />
                <span className="absolute bottom-1 right-1 px-1 py-0.5 text-[9px] font-bold rounded bg-black/60 text-white font-mono">
                  📷 3
                </span>
              </div>
            </div>

            <div className="text-xs font-bold text-slate-900">AI Labels</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Photos are integrated</div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-2 mt-3">
            <button
              onClick={() => handleApprove(incidents[1]?.id || 'inc-2')}
              className="py-1.5 px-3 rounded-xl bg-[#10b981] hover:bg-[#059669] text-white text-xs font-semibold shadow-sm transition-all text-center active:scale-95 cursor-pointer"
            >
              Approve
            </button>
            <button
              onClick={() => handleReject(incidents[1]?.id || 'inc-2')}
              className="py-1.5 px-3 rounded-xl bg-slate-200/80 hover:bg-slate-300 text-slate-700 text-xs font-semibold border border-slate-300/80 transition-all text-center active:scale-95 cursor-pointer"
            >
              Reject
            </button>
          </div>
        </div>

        {/* Card 3: AI Targets Precise Card */}
        <div className="bg-white/40 backdrop-blur-md rounded-2xl p-3 flex flex-col justify-between border border-white/80 shadow-sm hover:border-emerald-300 transition-all">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
                <Sparkles className="w-4 h-4 text-emerald-600" />
                <span>AI Labels</span>
              </div>
              <MoreHorizontal className="w-4 h-4 text-slate-400" />
            </div>

            <div className="h-24 flex items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500/10 to-teal-500/10 mb-2 border border-emerald-500/20 shadow-inner">
              <Sparkles className="w-10 h-10 text-[#10b981]/40 animate-pulse" />
            </div>

            <div className="text-xs font-bold text-slate-900">AI Labels</div>
            <div className="text-[10px] text-slate-500 mt-0.5">AI targets : precise</div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-2 mt-3">
            <button
              onClick={() => handleApprove(incidents[2]?.id || 'inc-3')}
              className="py-1.5 px-3 rounded-xl bg-[#10b981] hover:bg-[#059669] text-white text-xs font-semibold shadow-sm transition-all text-center active:scale-95 cursor-pointer"
            >
              Approve
            </button>
            <button
              onClick={() => handleReject(incidents[2]?.id || 'inc-3')}
              className="py-1.5 px-3 rounded-xl bg-slate-200/80 hover:bg-slate-300 text-slate-700 text-xs font-semibold border border-slate-300/80 transition-all text-center active:scale-95 cursor-pointer"
            >
              Reject
            </button>
          </div>
        </div>

      </div>

      {/* Spacer */}
      <div />
    </div>
  );
};
