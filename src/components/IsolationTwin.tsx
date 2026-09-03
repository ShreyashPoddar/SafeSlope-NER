import React from 'react';
import { MoreHorizontal, User, Building2, Cross } from 'lucide-react';
import type { IsolationStats, RoadDisconnect } from '../types/dashboard';

interface IsolationTwinProps {
  stats: IsolationStats;
  roadDisconnects: RoadDisconnect[];
  onFocusMap?: (lat: number, lng: number, name?: string) => void;
}

export const IsolationTwin: React.FC<IsolationTwinProps> = ({
  stats,
  onFocusMap
}) => {
  return (
    <div className="glass-panel-light rounded-3xl p-5 flex flex-col h-[390px] justify-between">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-base font-bold text-slate-800 tracking-tight">
          Critical Isolation
        </h2>
        <button className="text-slate-400 hover:text-slate-600 transition-colors p-1">
          <MoreHorizontal className="w-5 h-5" />
        </button>
      </div>

      {/* Main Content Grid: Inner Box on Left for 3 Demographic Cards + 2 Road Cut Cards on Right */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center my-auto">
        
        {/* Inner Container Box wrapping 3 Demographic Metric Cards together */}
        <div className="md:col-span-7 glass-panel-inner rounded-2xl p-2.5 flex items-center justify-between gap-2 shadow-inner">
          
          {/* Card 1: Isolated Population */}
          <div className="flex-1 bg-white/50 backdrop-blur-md rounded-xl p-2.5 flex flex-col items-center justify-between text-center border border-white/80 shadow-sm hover:border-emerald-300 transition-all">
            <div className="w-7 h-7 rounded-full bg-emerald-100/80 flex items-center justify-center text-[#10b981] mb-2">
              <User className="w-4 h-4 fill-[#10b981]" />
            </div>
            <div className="text-[10px] font-semibold text-slate-600 leading-tight mb-2">
              Isolated Population
            </div>
            <div className="text-xl font-black text-slate-900 font-sans">
              {stats.isolatedPopulation ?? 12450}
            </div>
          </div>

          {/* Card 2: Cut-off Villages */}
          <div className="flex-1 bg-white/50 backdrop-blur-md rounded-xl p-2.5 flex flex-col items-center justify-between text-center border border-white/80 shadow-sm hover:border-emerald-300 transition-all">
            <div className="w-7 h-7 rounded-full bg-emerald-100/80 flex items-center justify-center text-[#10b981] mb-2">
              <Building2 className="w-4 h-4 text-[#10b981]" />
            </div>
            <div className="text-[10px] font-semibold text-slate-600 leading-tight mb-2">
              Cut-off Villages
            </div>
            <div className="text-xl font-black text-slate-900 font-sans">
              {stats.cutoffVillagesCount ?? 20}
            </div>
          </div>

          {/* Card 3: Stranded PHCs */}
          <div className="flex-1 bg-white/50 backdrop-blur-md rounded-xl p-2.5 flex flex-col items-center justify-between text-center border border-white/80 shadow-sm hover:border-emerald-300 transition-all">
            <div className="w-7 h-7 rounded-full bg-emerald-100/80 flex items-center justify-center text-[#10b981] mb-2">
              <Cross className="w-4 h-4 text-[#10b981]" />
            </div>
            <div className="text-[10px] font-semibold text-slate-600 leading-tight mb-2">
              Stranded PHCs
            </div>
            <div className="text-xl font-black text-slate-900 font-sans">
              {stats.strandedPhcCount ?? 4}
            </div>
          </div>

        </div>

        {/* Right Side: 2 Road Cutoff Cards (NER Highway Cuts) */}
        <div className="md:col-span-5 grid grid-cols-2 gap-2.5">
          
          {/* Road Cut Card 1: NH-6 Sonapur Cut */}
          <div className="bg-white/40 backdrop-blur-md rounded-2xl p-3 flex flex-col justify-between border border-white/80 shadow-sm">
            <div>
              <h3 className="text-xs font-bold text-slate-900 truncate">
                NH-6 Sonapur Cut
              </h3>
              <p className="text-[10px] text-slate-500 mt-1 leading-snug">
                Asymmetrical barrier units
              </p>
            </div>

            <button
              onClick={() => onFocusMap && onFocusMap(23.7380, 92.7090)}
              className="mt-3 w-full py-1.5 px-2 rounded-xl bg-slate-200/80 hover:bg-slate-300 text-slate-700 text-[11px] font-semibold transition-all border border-slate-300/80 text-center active:scale-95 cursor-pointer"
            >
              Focus Map
            </button>
          </div>

          {/* Road Cut Card 2: NH-54 Aizawl Cut */}
          <div className="bg-white/40 backdrop-blur-md rounded-2xl p-3 flex flex-col justify-between border border-white/80 shadow-sm">
            <div>
              <h3 className="text-xs font-bold text-slate-900 truncate">
                NH-54 Aizawl ...
              </h3>
              <p className="text-[10px] text-slate-500 mt-1 leading-snug">
                Asymmetrical under cards
              </p>
            </div>

            <button
              onClick={() => onFocusMap && onFocusMap(23.7210, 92.7210)}
              className="mt-3 w-full py-1.5 px-2 rounded-xl bg-slate-200/80 hover:bg-slate-300 text-slate-700 text-[11px] font-semibold transition-all border border-slate-300/80 text-center active:scale-95 cursor-pointer"
            >
              Focus Map
            </button>
          </div>

        </div>

      </div>

      {/* Spacer */}
      <div />
    </div>
  );
};
