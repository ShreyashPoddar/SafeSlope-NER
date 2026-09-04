import React from 'react';
import { Printer, ArrowLeft, Download, Landmark } from 'lucide-react';
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
    <div className="min-h-screen bg-slate-200 print:bg-white text-slate-900 font-serif flex flex-col p-4 md:p-8 selection:bg-slate-900 selection:text-white">
      
      {/* Top Action Toolbar (Visible on Screen, Hidden during Print) */}
      <div className="max-w-4xl w-full mx-auto flex flex-wrap items-center justify-between gap-4 mb-6 print:hidden font-sans">
        <div className="flex items-center gap-3">
          {onBackToDashboard && (
            <button
              onClick={onBackToDashboard}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white hover:bg-slate-50 text-slate-900 text-xs font-bold transition-all border border-slate-400 shadow-sm cursor-pointer active:scale-95"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Return to Dashboard</span>
            </button>
          )}
          <span className="px-3 py-1 text-xs font-bold rounded bg-slate-900 text-white font-mono uppercase tracking-wider">
            OFFICIAL GAZETTE FORMAT
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* PDF Download Link */}
          <PDFDownloadLink
            document={<EvacuationSOPDocument stats={stats} />}
            fileName={`SDMA_NER_Order_${new Date().toISOString().slice(0, 10)}.pdf`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-900 text-white text-xs font-bold transition-all shadow-md active:scale-95 cursor-pointer"
          >
            {({ loading }) => (
              <>
                <Download className="w-4 h-4" />
                <span>{loading ? 'Compiling PDF...' : 'Download PDF Document'}</span>
              </>
            )}
          </PDFDownloadLink>

          {/* Primary Print Button */}
          <button
            onClick={handlePrint}
            className="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-emerald-800 hover:bg-emerald-900 text-white text-xs font-bold shadow-md transition-all cursor-pointer active:scale-95"
          >
            <Printer className="w-4 h-4" />
            <span>Print Official Order (PDF)</span>
          </button>
        </div>
      </div>

      {/* Main Authentic Government Document Sheet Container */}
      <div className="max-w-4xl w-full mx-auto bg-white border-2 border-slate-900 p-8 md:p-14 shadow-2xl print:shadow-none print:border-none print:p-0 print:m-0 flex flex-col gap-6 text-slate-950 leading-normal">
        
        {/* Header & Official Crest */}
        <header className="flex flex-col items-center text-center border-b-2 border-slate-900 pb-6">
          {/* State Emblem Placeholder */}
          <div className="w-16 h-16 rounded-full border-2 border-slate-900 flex items-center justify-center text-slate-900 mb-3">
            <Landmark className="w-9 h-9" />
          </div>
          
          <h1 className="text-base md:text-lg font-bold uppercase tracking-widest text-slate-900">
            GOVERNMENT OF INDIA
          </h1>
          <h2 className="text-sm md:text-base font-bold uppercase tracking-wider text-slate-900 mt-0.5">
            STATE DISASTER MANAGEMENT AUTHORITY (SDMA)
          </h2>
          <h3 className="text-xs md:text-sm font-semibold uppercase tracking-wider text-slate-800 mt-0.5">
            MINISTRY OF NORTH EASTERN REGION CONTROL ROOM
          </h3>

          {/* Order Reference & Date Margin Block */}
          <div className="w-full flex items-center justify-between border-t border-slate-900 mt-5 pt-2 text-xs font-mono font-bold">
            <div>ORDER NO: SDMA/NER/2026/SL-087</div>
            <div>DATE: September 04, 2026</div>
          </div>
        </header>

        {/* Document Title & Preamble */}
        <section className="flex flex-col gap-3 text-center my-1">
          <h2 className="text-base md:text-lg font-black uppercase tracking-wider text-slate-900 underline underline-offset-4">
            EMERGENCY DISPATCH ORDER (SECTION 30, DISASTER MANAGEMENT ACT)
          </h2>
          
          <div className="text-xs md:text-sm font-bold text-left uppercase tracking-wide mt-1">
            SUBJECT: Mandatory Evacuation &amp; Tactical Relief Dispatch for NH-6 Sonapur Landslide Cut-off.
          </div>

          <p className="text-xs md:text-sm text-justify leading-relaxed font-serif mt-1">
            Whereas, continuous real-time geotechnical telemetry and satellite radar monitoring have indicated severe structural instability (exceeding 87% failure probability) along the NH-6 Sonapur corridor; now, therefore, in exercise of the powers conferred under Section 30 of the Disaster Management Act, 2005, the undersigned hereby issues the following mandatory executive directives for immediate execution by all line departments and emergency response units.
          </p>
        </section>

        {/* SECTION I: Operational Incident Context (Formal Grid Table) */}
        <section className="flex flex-col gap-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 font-sans">
            SECTION I: OPERATIONAL INCIDENT CONTEXT
          </h3>

          <table className="w-full border-collapse border-2 border-slate-900 text-xs text-left">
            <tbody>
              <tr className="border-b border-slate-900">
                <td className="w-1/3 p-2.5 font-bold bg-slate-100 border-r border-slate-900 uppercase">
                  Affected Sector
                </td>
                <td className="w-2/3 p-2.5 font-semibold">
                  NH-6 Sonapur Corridor (Milepost 42 to 48)
                </td>
              </tr>
              <tr className="border-b border-slate-900">
                <td className="p-2.5 font-bold bg-slate-100 border-r border-slate-900 uppercase">
                  Threat Classification
                </td>
                <td className="p-2.5 font-bold text-rose-700">
                  LEVEL 3: CRITICAL RED ALERT (Geotechnical Instability &gt; 87%)
                </td>
              </tr>
              <tr className="border-b border-slate-900">
                <td className="p-2.5 font-bold bg-slate-100 border-r border-slate-900 uppercase">
                  Isolated Population
                </td>
                <td className="p-2.5 font-semibold">
                  {stats.isolatedPopulation?.toLocaleString() ?? '12,450'} Residents across {stats.cutoffVillagesCount ?? 20} NER Hill Villages
                </td>
              </tr>
              <tr>
                <td className="p-2.5 font-bold bg-slate-100 border-r border-slate-900 uppercase">
                  Primary Transport Status
                </td>
                <td className="p-2.5 font-semibold">
                  NH-6 Fully Severed; Active Detour Route (+{stats.detourKm ?? 42.5} km via SH-12)
                </td>
              </tr>
            </tbody>
          </table>
        </section>

        {/* SECTION II: Mandatory Operational Protocols (Official Table Format) */}
        <section className="flex flex-col gap-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 font-sans">
            SECTION II: MANDATORY OPERATIONAL PROTOCOLS
          </h3>

          <table className="w-full border-collapse border-2 border-slate-900 text-xs text-left">
            <thead>
              <tr className="border-b-2 border-slate-900 bg-slate-100 uppercase font-bold text-slate-900">
                <th className="p-2.5 border-r border-slate-900 w-1/6">Trigger Level</th>
                <th className="p-2.5 border-r border-slate-900 w-1/4">Geotechnical Threshold</th>
                <th className="p-2.5 border-r border-slate-900 w-5/12">Mandatory Executive Directives</th>
                <th className="p-2.5 w-1/6">Assigned Unit</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-900">
                <td className="p-2.5 border-r border-slate-900 font-bold uppercase">
                  Level 1 (Alert)
                </td>
                <td className="p-2.5 border-r border-slate-900 font-mono text-[11px]">
                  Tilt acceleration &gt; 2.5 mm/hr
                </td>
                <td className="p-2.5 border-r border-slate-900">
                  Issue Emergency SMS Broadcast &amp; Initiate Continuous Satellite Radar Tracking
                </td>
                <td className="p-2.5 font-semibold">
                  Geological Survey / NIC Cell
                </td>
              </tr>
              <tr className="border-b border-slate-900">
                <td className="p-2.5 border-r border-slate-900 font-bold uppercase">
                  Level 2 (Evacuate)
                </td>
                <td className="p-2.5 border-r border-slate-900 font-mono text-[11px]">
                  Soil Moisture Saturation &gt; 60%
                </td>
                <td className="p-2.5 border-r border-slate-900">
                  Enforce Mandatory Sector Evacuation &amp; Erect Traffic Diversions (+42.5 km bypass)
                </td>
                <td className="p-2.5 font-semibold">
                  District Police &amp; BRO
                </td>
              </tr>
              <tr>
                <td className="p-2.5 border-r border-slate-900 font-bold uppercase">
                  Level 3 (Rescue/Relief)
                </td>
                <td className="p-2.5 border-r border-slate-900 font-mono text-[11px]">
                  NH-6 Roadway Severance
                </td>
                <td className="p-2.5 border-r border-slate-900">
                  Deploy Heavy Machinery for Debris Clearance &amp; Initiate Airdrop of Essential Supplies
                </td>
                <td className="p-2.5 font-semibold">
                  NDRF / SDRF / IAF Aviation
                </td>
              </tr>
            </tbody>
          </table>
        </section>

        {/* SECTION III: Official Authorization & Sign-Off Block */}
        <section className="mt-4 pt-4 border-t-2 border-slate-900 flex flex-col gap-6">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 font-sans">
            SECTION III: AUTHORIZATION &amp; ISSUANCE
          </h3>

          <div className="grid grid-cols-2 gap-10 text-xs">
            {/* Signature Left */}
            <div className="flex flex-col justify-end pt-12">
              <div className="border-t border-slate-900 pt-1.5 font-bold uppercase">
                (Dr. Lalrinpuia Sailo, IAS)
              </div>
              <div className="text-[11px] text-slate-800">
                Nodal Officer, SDMA North East Region
              </div>
            </div>

            {/* Signature Right */}
            <div className="flex flex-col justify-end pt-12 text-right">
              <div className="border-t border-slate-900 pt-1.5 font-bold uppercase">
                (Smt. Zoramthangi Lunglei, IAS)
              </div>
              <div className="text-[11px] text-slate-800">
                State Disaster Relief Commissioner &amp; Chairperson
              </div>
            </div>
          </div>

          {/* Official Rectangular SDMA Emergency Stamp/Seal Box */}
          <div className="mx-auto my-2 p-3 border-2 border-dashed border-slate-900 text-center uppercase text-[11px] font-mono font-bold max-w-sm">
            [ SDMA EMERGENCY SEAL / STAMP ]
            <div className="text-[9px] font-normal text-slate-700 mt-0.5">
              Verified Control Room Record • SHA-256 Verified
            </div>
          </div>
        </section>

        {/* SECTION IV: Endorsement & Distribution List (Copy To) */}
        <section className="border-t border-slate-900 pt-4 text-xs">
          <div className="font-bold uppercase tracking-wide mb-1">
            COPY TO FOR IMMEDIATE INFORMATION AND COMPLIANCE:
          </div>
          <ol className="list-decimal pl-5 space-y-0.5 font-serif text-[11px]">
            <li>Office of the District Magistrate &amp; Collector, Aizawl / East Khasi Hills.</li>
            <li>Chief Engineer, Border Roads Organisation (BRO), Project Pushpak / Swastik.</li>
            <li>Commandant, 1st Battalion National Disaster Response Force (NDRF).</li>
            <li>Guard File / Command Center Operations Log.</li>
          </ol>
        </section>

      </div>

    </div>
  );
};
