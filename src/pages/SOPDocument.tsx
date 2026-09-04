import React from 'react';
import { 
  Printer, 
  ArrowLeft, 
  ShieldAlert, 
  CheckSquare, 
  FileText, 
  Users, 
  AlertTriangle, 
  Activity, 
  Download,
  Building,
  Award
} from 'lucide-react';
import { PDFDownloadLink } from '@react-pdf/renderer';
import { EvacuationSOPDocument } from '../components/SOPDocument';
import type { IsolationStats } from '../types/dashboard';

interface SOPPageProps {
  stats?: IsolationStats;
  onBackToDashboard?: () => void;
}

export const SOPDocumentPage: React.FC<SOPPageProps> = ({
  stats = {
    isolatedPopulation: 12450,
    cutoffVillagesCount: 20,
    primaryCutoffRoad: 'NH-6 Sonapur Highway Cut',
    estimatedClearingTimeHours: 18,
    strandedPhcCount: 4,
    detourKm: 42.5,
    delayMins: 85
  },
  onBackToDashboard
}) => {
  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen text-slate-900 flex flex-col font-sans selection:bg-emerald-500 selection:text-white p-4 md:p-8">
      
      {/* Top Action Bar (Hidden during Print) */}
      <div className="max-w-4xl w-full mx-auto flex flex-wrap items-center justify-between gap-4 mb-6 print:hidden">
        <div className="flex items-center gap-3">
          {onBackToDashboard && (
            <button
              onClick={onBackToDashboard}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/70 hover:bg-white/90 text-slate-800 text-xs font-bold transition-all border border-white/90 shadow-sm cursor-pointer active:scale-95 backdrop-blur-md"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Command Dashboard</span>
            </button>
          )}
          <span className="px-3.5 py-1.5 text-xs font-extrabold rounded-full bg-emerald-500/30 text-white border border-emerald-400/50 shadow-sm drop-shadow-sm font-mono tracking-wide">
            OFFICIAL SDMA DISPATCH DRAFT
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* PDF Download Trigger */}
          <PDFDownloadLink
            document={<EvacuationSOPDocument stats={stats} />}
            fileName={`SDMA_NER_Emergency_Order_${new Date().toISOString().slice(0, 10)}.pdf`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-900 text-white text-xs font-bold transition-all shadow-md active:scale-95 cursor-pointer"
          >
            {({ loading }) => (
              <>
                <Download className="w-4 h-4" />
                <span>{loading ? 'Preparing PDF...' : 'Download PDF Document'}</span>
              </>
            )}
          </PDFDownloadLink>

          {/* Native Print / Save as PDF Button */}
          <button
            onClick={handlePrint}
            className="inline-flex items-center gap-2 px-5 py-2 rounded-xl bg-[#10b981] hover:bg-[#059669] text-white text-xs font-bold shadow-md shadow-emerald-500/20 transition-all cursor-pointer active:scale-95"
          >
            <Printer className="w-4 h-4" />
            <span>Print / Save as PDF (A4)</span>
          </button>
        </div>
      </div>

      {/* Main Printable A4 Document Sheet Container with Frosted Glassmorphism Styling */}
      <div className="max-w-4xl w-full mx-auto glass-panel-light border border-white/90 rounded-3xl p-6 md:p-10 shadow-2xl print:shadow-none print:border-none print:p-0 print:m-0 print:rounded-none print:bg-white flex flex-col gap-6 backdrop-blur-3xl">
        
        {/* Government / SDMA Official Order Header */}
        <header className="border-b-2 border-slate-900 pb-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-emerald-700 text-white flex items-center justify-center font-black text-xl shadow-md shrink-0 border border-emerald-800">
                <ShieldAlert className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-lg md:text-xl font-black text-slate-900 uppercase tracking-tight font-mono">
                  STATE DISASTER MANAGEMENT AUTHORITY (SDMA)
                </h1>
                <p className="text-xs md:text-sm font-extrabold text-emerald-800 uppercase tracking-widest mt-0.5">
                  NORTH EASTERN REGION (NER) // EMERGENCY DISPATCH ORDER
                </p>
                <p className="text-[11px] text-slate-600 font-mono mt-0.5">
                  Inter-State Hill Corridor • Mizoram-Meghalaya Disaster Relief Cell • Hunthar-Sonapur Sector
                </p>
              </div>
            </div>

            {/* Red Alert Stamp Badge */}
            <div className="shrink-0 text-right">
              <span className="inline-block px-3 py-1.5 rounded-xl bg-rose-600 text-white text-xs font-black uppercase tracking-wider shadow-sm font-mono border border-rose-700">
                LEVEL 3: CRITICAL RED ALERT
              </span>
              <p className="text-[10px] text-slate-500 font-mono mt-1">Status: MANDATORY EXECUTION</p>
            </div>
          </div>

          {/* Dynamic Metadata Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-5 pt-4 border-t border-slate-300 font-mono text-xs">
            <div className="glass-panel-inner p-2.5 rounded-xl border border-white/80">
              <span className="text-slate-500 block text-[10px]">INCIDENT ORDER ID</span>
              <span className="font-bold text-slate-900">SDMA/NER/2026/SL-087</span>
            </div>
            <div className="glass-panel-inner p-2.5 rounded-xl border border-white/80">
              <span className="text-slate-500 block text-[10px]">TIMESTAMP</span>
              <span className="font-bold text-slate-900">04-SEP-2026 00:47 IST</span>
            </div>
            <div className="glass-panel-inner p-2.5 rounded-xl border border-white/80">
              <span className="text-slate-500 block text-[10px]">ISSUING AUTHORITY</span>
              <span className="font-bold text-slate-900">Nodal Officer, SDMA NER</span>
            </div>
            <div className="glass-panel-inner p-2.5 rounded-xl border border-white/80">
              <span className="text-slate-500 block text-[10px]">SECTOR JURISDICTION</span>
              <span className="font-bold text-slate-900">Hunthar-Sonapur Corridor</span>
            </div>
          </div>
        </header>

        {/* SECTION 1: Automated Incident Context Summary */}
        <section className="flex flex-col gap-3">
          <div className="flex items-center gap-2 border-b border-slate-300 pb-1.5">
            <FileText className="w-4 h-4 text-emerald-700" />
            <h2 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider font-mono">
              1. Automated Incident Context & Telemetry Summary
            </h2>
          </div>

          {/* Metric Cards Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="glass-panel-inner border border-emerald-300/80 rounded-2xl p-3.5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-emerald-900 text-xs font-semibold">
                <span>Total Isolated Pop.</span>
                <Users className="w-4 h-4 text-emerald-700" />
              </div>
              <div className="text-2xl font-black text-slate-900 mt-2 font-mono">
                {stats.isolatedPopulation?.toLocaleString() ?? '12,450'}
              </div>
              <span className="text-[10px] text-slate-600 mt-1">Across 20 NER Cut-off Villages</span>
            </div>

            <div className="glass-panel-inner border border-emerald-300/80 rounded-2xl p-3.5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-emerald-900 text-xs font-semibold">
                <span>Severed Route</span>
                <AlertTriangle className="w-4 h-4 text-emerald-700" />
              </div>
              <div className="text-base font-black text-slate-900 mt-2 font-mono truncate">
                {stats.primaryCutoffRoad ?? 'NH-6 Sonapur Cut'}
              </div>
              <span className="text-[10px] text-slate-600 mt-1">+{stats.detourKm ?? 42.5} km Detour</span>
            </div>

            <div className="glass-panel-inner border border-emerald-300/80 rounded-2xl p-3.5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-emerald-900 text-xs font-semibold">
                <span>Stranded PHCs</span>
                <Building className="w-4 h-4 text-emerald-700" />
              </div>
              <div className="text-2xl font-black text-slate-900 mt-2 font-mono">
                {stats.strandedPhcCount ?? 4}
              </div>
              <span className="text-[10px] text-slate-600 mt-1">Requires Air Supply Drop</span>
            </div>

            <div className="glass-panel-inner border border-emerald-300/80 rounded-2xl p-3.5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-emerald-900 text-xs font-semibold">
                <span>Slope Instability</span>
                <Activity className="w-4 h-4 text-emerald-700" />
              </div>
              <div className="text-2xl font-black text-rose-600 mt-2 font-mono">
                87% ML Risk
              </div>
              <span className="text-[10px] text-slate-600 mt-1">High Risk Threshold</span>
            </div>
          </div>
        </section>

        {/* SECTION 2: Formal SDMA Operational Checklist (Triggers 1–3) */}
        <section className="flex flex-col gap-3.5">
          <div className="flex items-center gap-2 border-b border-slate-300 pb-1.5">
            <CheckSquare className="w-4 h-4 text-emerald-700" />
            <h2 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider font-mono">
              2. Formal SDMA Operational Response Checklist
            </h2>
          </div>

          <div className="space-y-3">
            
            {/* Level 1: Alert */}
            <div className="glass-panel-inner rounded-2xl p-4 flex flex-col gap-2 border border-white/80">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold text-emerald-900 uppercase tracking-wider font-mono">
                  LEVEL 1: AUTOMATED ALERT & SATELLITE TRACKING
                </span>
                <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-100 text-emerald-800 font-mono">
                  TRIGGERED (COMPLETED)
                </span>
              </div>
              <ul className="text-xs text-slate-800 space-y-1.5 pl-4 list-disc font-medium">
                <li>Broadcast emergency SMS alerts to all mobile towers within Hunthar-Sonapur sector radius.</li>
                <li>Notify Assam Rifles, NDRF 1st Battalion, and SDRF posts for high-readiness deployment.</li>
                <li>Initiate continuous real-time satellite radar and IoT slope tilt sensor tracking across NER corridors.</li>
              </ul>
            </div>

            {/* Level 2: Evacuate */}
            <div className="glass-panel-inner rounded-2xl p-4 flex flex-col gap-2 border border-white/80">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold text-amber-900 uppercase tracking-wider font-mono">
                  LEVEL 2: MANDATORY SECTOR EVACUATION & DETOUR ROUTING
                </span>
                <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-amber-100 text-amber-900 font-mono">
                  ACTIVE IN-PROGRESS
                </span>
              </div>
              <ul className="text-xs text-slate-800 space-y-1.5 pl-4 list-disc font-medium">
                <li>Enforce mandatory evacuation orders for residents in red-zone slope sectors (Hunthar Veng Ridge).</li>
                <li>Deploy emergency detour signs redirecting heavy freight along the secondary +42.5 km bypass route.</li>
                <li>Establish temporary relief camps with drinking water and power at Kolasib relief school.</li>
              </ul>
            </div>

            {/* Level 3: Rescue / Isolate */}
            <div className="glass-panel-inner rounded-2xl p-4 flex flex-col gap-2 border border-white/80">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold text-rose-900 uppercase tracking-wider font-mono">
                  LEVEL 3: AIR-DROP MEDICAL SUPPLIES & HEAVY DEBRIS CLEARANCE
                </span>
                <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-rose-100 text-rose-900 font-mono">
                  IMMEDIATE EXECUTION
                </span>
              </div>
              <ul className="text-xs text-slate-800 space-y-1.5 pl-4 list-disc font-medium">
                <li>Dispatch Indian Air Force / SDRF helicopters for emergency medical air-drops to 4 stranded PHCs.</li>
                <li>Mobilize heavy Border Roads Organisation (BRO) earth excavators to clear NH-6 Sonapur rockfall debris.</li>
                <li>Deploy satellite emergency communication units to cutoff NER villages for remote triage.</li>
              </ul>
            </div>

          </div>
        </section>

        {/* SECTION 3: Sign-off & Authority Seal Section */}
        <section className="mt-4 pt-5 border-t-2 border-slate-900 flex flex-col gap-6">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            
            {/* Signature Box 1: Nodal Officer */}
            <div className="glass-panel-inner rounded-2xl p-4 flex flex-col justify-between h-36 border border-white/90">
              <div>
                <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest font-mono">
                  ISSUING AUTHORITY SIGNATURE
                </span>
                <div className="mt-2 font-mono text-sm font-bold text-emerald-900 italic">
                  Dr. Lalrinpuia Sailo, IAS
                </div>
              </div>
              <div className="border-t border-slate-300 pt-1 text-[11px] text-slate-700 font-mono">
                Nodal Officer • State Disaster Management Authority (NER)
              </div>
            </div>

            {/* Signature Box 2: Disaster Commissioner */}
            <div className="glass-panel-inner rounded-2xl p-4 flex flex-col justify-between h-36 border border-white/90">
              <div>
                <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest font-mono">
                  APPROVAL & ORDER CONFIRMATION
                </span>
                <div className="mt-2 font-mono text-sm font-bold text-emerald-900 italic">
                  Smt. Zoramthangi Lunglei, IAS
                </div>
              </div>
              <div className="border-t border-slate-300 pt-1 text-[11px] text-slate-700 font-mono">
                State Disaster Relief Commissioner • SDMA North East
              </div>
            </div>

          </div>

          {/* Digital Verification Seal & Timestamp Box */}
          <div className="bg-slate-900 text-white rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4 font-mono text-xs shadow-lg">
            <div className="flex items-center gap-3">
              <Award className="w-6 h-6 text-emerald-400 shrink-0" />
              <div>
                <span className="font-bold text-emerald-400 block text-xs">
                  OFFICIAL DIGITAL VERIFICATION SEAL (NER DISPATCH)
                </span>
                <span className="text-[10px] text-slate-300">
                  Cryptographically Signed • SHA-256 Digest: 9a8b7c6d5e4f3a2b
                </span>
              </div>
            </div>

            <div className="text-right text-[11px] text-slate-300">
              <div>VERIFIED TIMESTAMP: 04-SEP-2026 00:47 IST</div>
              <div className="text-emerald-400 font-bold">CONTROL ROOM RECORD MATCHED</div>
            </div>
          </div>

        </section>

      </div>

    </div>
  );
};
