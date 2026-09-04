import React, { useState } from 'react';
import { 
  Filter, 
  Search, 
  AlertOctagon, 
  ShieldCheck, 
  User, 
  Compass, 
  Layers, 
  Clock, 
  MapPin, 
  AlertTriangle,
  FileCheck2,
  XCircle
} from 'lucide-react';
import type { CitizenIncident } from '../types/dashboard';

interface ModerationQueuePanelProps {
  incidents: CitizenIncident[];
  selectedId: string | null;
  onSelectIncident: (id: string) => void;
  activeFilter: 'all' | 'unverified' | 'cluster';
  onFilterChange: (filter: 'all' | 'unverified' | 'cluster') => void;
}

export const ModerationQueuePanel: React.FC<ModerationQueuePanelProps> = ({
  incidents,
  selectedId,
  onSelectIncident,
  activeFilter,
  onFilterChange
}) => {
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Filter logic
  const filteredIncidents = incidents.filter(item => {
    // Search query filter
    const queryMatch = searchQuery === '' || 
      item.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.locationName && item.locationName.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (item.tag && item.tag.toLowerCase().includes(searchQuery.toLowerCase()));

    if (!queryMatch) return false;

    if (activeFilter === 'unverified') {
      return item.verificationStatus === 'unverified' || !item.verificationStatus;
    }
    if (activeFilter === 'cluster') {
      return item.isClusterFlagged === true;
    }
    return true; // 'all'
  });

  const getStatusBadge = (item: CitizenIncident) => {
    const status = item.verificationStatus || (item.status === 'approved' ? 'approved' : 'unverified');
    switch (status) {
      case 'verified_onsite':
        return (
          <span className="bg-emerald-100 text-[#10b981] border border-emerald-300 text-[10px] font-black px-2 py-0.5 rounded-full flex items-center gap-1">
            <FileCheck2 className="w-3 h-3" />
            <span>Verified On-Site</span>
          </span>
        );
      case 'approved':
        return (
          <span className="bg-emerald-600 text-white text-[10px] font-black px-2 py-0.5 rounded-full flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-white" />
            <span>Published</span>
          </span>
        );
      case 'false_alarm':
        return (
          <span className="bg-rose-100 text-rose-700 border border-rose-300 text-[10px] font-black px-2 py-0.5 rounded-full flex items-center gap-1">
            <XCircle className="w-3 h-3" />
            <span>False Alarm</span>
          </span>
        );
      default:
        return (
          <span className="bg-amber-100 text-amber-900 border border-amber-300 text-[10px] font-black px-2 py-0.5 rounded-full flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>Unverified</span>
          </span>
        );
    }
  };

  return (
    <div className="glass-panel-light rounded-3xl p-4 sm:p-5 flex flex-col h-[760px] border border-white/80 shadow-xl overflow-hidden">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-[#10b981] text-white flex items-center justify-center font-bold">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-black text-slate-900 tracking-tight">
              Ingestion Queue
            </h2>
            <p className="text-[10px] font-mono text-slate-500">
              {filteredIncidents.length} Incoming Hazard Reports
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1 text-[11px] font-bold text-slate-500">
          <Filter className="w-3.5 h-3.5" />
          <span>Filter</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="grid grid-cols-3 gap-1 bg-slate-200/80 p-1 rounded-2xl border border-slate-300 my-3">
        <button
          onClick={() => onFilterChange('all')}
          className={`py-1.5 px-2 rounded-xl text-xs font-bold transition-all text-center ${
            activeFilter === 'all' 
              ? 'bg-[#10b981] text-white shadow-sm' 
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          All ({incidents.length})
        </button>
        <button
          onClick={() => onFilterChange('unverified')}
          className={`py-1.5 px-2 rounded-xl text-xs font-bold transition-all text-center ${
            activeFilter === 'unverified' 
              ? 'bg-[#10b981] text-white shadow-sm' 
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Unverified ({incidents.filter(i => i.verificationStatus === 'unverified' || !i.verificationStatus).length})
        </button>
        <button
          onClick={() => onFilterChange('cluster')}
          className={`py-1.5 px-2 rounded-xl text-xs font-bold transition-all text-center ${
            activeFilter === 'cluster' 
              ? 'bg-[#10b981] text-white shadow-sm' 
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Flagged ({incidents.filter(i => i.isClusterFlagged).length})
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative mb-3">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
        <input
          type="text"
          placeholder="Search by ID, location, or tag..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] focus:ring-2 focus:ring-[#10b981]/20 rounded-xl pl-9 pr-3 py-1.5 text-xs font-semibold text-slate-800"
        />
      </div>

      {/* Incident List Queue */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
        {filteredIncidents.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400">
            <AlertOctagon className="w-10 h-10 mb-2 opacity-50" />
            <p className="text-xs font-bold">No hazard reports match your filter criteria.</p>
          </div>
        ) : (
          filteredIncidents.map((item) => {
            const isSelected = item.id === selectedId;
            return (
              <div
                key={item.id}
                onClick={() => onSelectIncident(item.id)}
                className={`p-3.5 rounded-2xl transition-all cursor-pointer border ${
                  isSelected
                    ? 'bg-emerald-50/90 border-[#10b981] shadow-lg shadow-emerald-500/10 ring-2 ring-[#10b981]/30'
                    : 'bg-white/80 border-slate-200/80 hover:border-emerald-300 hover:bg-white'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-black text-slate-900">
                      {item.id}
                    </span>
                    <span className="bg-slate-900 text-emerald-400 text-[10px] font-black px-2 py-0.5 rounded-md uppercase">
                      {item.tag}
                    </span>
                  </div>

                  {getStatusBadge(item)}
                </div>

                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800 mt-2">
                  <MapPin className="w-3.5 h-3.5 text-[#10b981] shrink-0" />
                  <span className="truncate">{item.locationName || 'Unmapped Coordinate'}</span>
                </div>

                {item.description && (
                  <p className="text-[11px] text-slate-600 line-clamp-2 mt-1 font-medium">
                    "{item.description}"
                  </p>
                )}

                {/* Card Footer Info */}
                <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] font-medium text-slate-500">
                  <div className="flex items-center gap-2">
                    {/* Reporter Persona Pill */}
                    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded font-bold ${
                      item.submissionPersona === 'Tourist / Traveler'
                        ? 'bg-amber-100 text-amber-900'
                        : 'bg-emerald-100 text-emerald-900'
                    }`}>
                      {item.submissionPersona === 'Tourist / Traveler' ? <Compass className="w-2.5 h-2.5" /> : <User className="w-2.5 h-2.5" />}
                      <span>{item.submissionPersona || 'Local Resident'}</span>
                    </span>

                    {/* Cluster Flagged Alert */}
                    {item.isClusterFlagged && (
                      <span className="bg-rose-100 text-rose-800 font-bold px-1.5 py-0.5 rounded flex items-center gap-1 animate-pulse">
                        <AlertTriangle className="w-2.5 h-2.5 text-rose-600" />
                        <span>Cluster &lt;500m</span>
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-1 text-slate-400 font-mono">
                    <Clock className="w-2.5 h-2.5" />
                    <span>{item.timestamp}</span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

    </div>
  );
};
