import React from 'react';
import { MoreHorizontal, Droplets } from 'lucide-react';
import type { TelemetryData } from '../types/dashboard';

interface TelemetryIndicatorsProps {
  telemetry: TelemetryData;
}

export const TelemetryIndicators: React.FC<TelemetryIndicatorsProps> = ({ telemetry }) => {
  return (
    <div className="glass-panel-light rounded-3xl p-5 flex flex-col h-[390px] justify-between">
      
      {/* Telemetry Card Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-base font-bold text-slate-800 tracking-tight">
          Telemetry
        </h2>
        <button className="text-slate-400 hover:text-slate-600 transition-colors p-1">
          <MoreHorizontal className="w-5 h-5" />
        </button>
      </div>

      {/* Centered Main Content Grid */}
      <div className="my-auto py-2 grid grid-cols-1 md:grid-cols-12 gap-5 items-center">
        
        {/* Left Side: X, Y, Z Multi-Axis Line Chart */}
        <div className="md:col-span-6 flex flex-col justify-center">
          <div className="relative h-44 w-full flex items-end">
            
            {/* Y-Axis Threshold Labels (150, 100, 50, 0) */}
            <div className="absolute left-0 top-0 bottom-0 flex flex-col justify-between text-[10px] font-medium text-slate-400 font-mono pr-2">
              <span>150</span>
              <span>100</span>
              <span>50</span>
              <span>0</span>
            </div>

            {/* SVG Line Chart */}
            <div className="w-full h-full ml-7 relative">
              <div className="absolute inset-0 flex flex-col justify-between pointer-events-none">
                <div className="w-full border-b border-slate-200/80" />
                <div className="w-full border-b border-slate-200/80" />
                <div className="w-full border-b border-slate-200/80" />
                <div className="w-full border-b border-slate-300" />
              </div>

              <svg className="w-full h-full overflow-visible" viewBox="0 0 200 120" preserveAspectRatio="none">
                <path
                  d="M 0 75 Q 30 70 60 40 T 120 70 T 180 50 T 200 55"
                  fill="none"
                  stroke="#a7f3d0"
                  strokeWidth="2.5"
                />
                <path
                  d="M 0 70 Q 40 75 70 60 T 130 90 T 180 40 T 200 45"
                  fill="none"
                  stroke="#10b981"
                  strokeWidth="3"
                />
                <path
                  d="M 0 80 Q 50 65 90 75 T 150 50 T 200 35"
                  fill="none"
                  stroke="#047857"
                  strokeWidth="2"
                />
              </svg>
            </div>

          </div>

          <div className="flex justify-between ml-7 text-[11px] font-mono font-medium text-slate-400 pt-1">
            <span>X</span>
            <span>Y</span>
            <span>Z</span>
          </div>
        </div>

        {/* Right Side: Soil Moisture Saturation & ML Hazard Risk */}
        <div className="md:col-span-6 flex flex-col justify-center gap-4">
          
          {/* Soil Moisture Saturation */}
          <div className="flex flex-col gap-1.5">
            <div className="text-xs font-semibold text-slate-700">
              Soil Moisture Saturation
            </div>

            <div className="w-full bg-slate-200/80 rounded-full h-2 overflow-hidden">
              <div className="bg-[#10b981] h-2 rounded-full w-[65%]" />
            </div>

            <div className="flex items-center justify-between pt-0.5">
              <div className="flex items-center gap-2">
                <span className="text-2xl font-black text-slate-900 tracking-tight font-sans">
                  {telemetry.moisturePercent ?? 65}%
                </span>
                <div className="w-6 h-6 rounded-full bg-[#10b981]/20 flex items-center justify-center text-[#10b981]">
                  <Droplets className="w-4 h-4 fill-[#10b981]" />
                </div>
              </div>
              <span className="text-xs font-semibold text-slate-500 font-mono">
                40 %
              </span>
            </div>
          </div>

          {/* ML Hazard Risk Alert */}
          <div className="flex flex-col gap-1.5 pt-2 border-t border-slate-200/80">
            <div>
              <div className="text-lg font-black text-slate-900 tracking-tight leading-tight">
                87% ML Hazard Risk
              </div>
              <div className="text-xs font-semibold text-slate-500">
                (High Risk)
              </div>
            </div>

            <div className="mt-0.5">
              <div className="text-[11px] font-semibold text-slate-500 mb-1">
                Confidence Index
              </div>
              <div className="w-full bg-slate-200/80 rounded-full h-2 overflow-hidden">
                <div className="bg-[#10b981] h-2 rounded-full w-[87%]" />
              </div>
            </div>
          </div>

        </div>

      </div>

      {/* Spacer */}
      <div />
    </div>
  );
};
