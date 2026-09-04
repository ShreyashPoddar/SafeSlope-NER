import React, { useState, useEffect, useCallback } from 'react';
import { 
  ShieldAlert, 
  ArrowLeft, 
  FileText, 
  Radio, 
  CheckCircle2, 
  AlertTriangle, 
  X, 
  Zap, 
  FileCheck2, 
  MessageSquare, 
  Volume2, 
  Smartphone
} from 'lucide-react';
import { ExecutiveDispatchPanel } from '../components/ExecutiveDispatchPanel';
import type { DispatchTask } from '../types/dashboard';
import { getIsolatedVillages } from '../api/villages';
import { authorizeEvacuationOrder } from '../api/governance';

interface DispatchCommandWorkspaceProps {
  onBackToDashboard?: () => void;
  onNavigateToSOP?: () => void;
}

// Initial mock inter-agency tasks
const initialDispatchTasks: DispatchTask[] = [
  {
    id: 'TASK-901',
    agency: 'BRO',
    taskName: 'Heavy Debris Clearing & Heavy Bulldozer Deployment',
    commanderName: 'Col. R. Sharma, BRO 763 BRTF',
    priority: 'Urgent',
    targetSector: 'NH-6 Sonapur Cut',
    timestamp: '10:15 IST',
    status: 'On-Site Ops Active'
  },
  {
    id: 'TASK-902',
    agency: 'NDRF',
    taskName: 'Zone 4 Residential Evacuation & Medical Escort',
    commanderName: 'Cmdt. V. K. Nair, 12 Bn NDRF',
    priority: 'Urgent',
    targetSector: 'Hunthar Veng Slope',
    timestamp: '10:08 IST',
    status: 'En Route'
  },
  {
    id: 'TASK-903',
    agency: 'IAF Cell',
    taskName: 'Air Reconnaissance & Emergency Medical Evacuation Helicopter',
    commanderName: 'Wg Cdr S. Roy, IAF Heli-Unit',
    priority: 'Standard',
    targetSector: 'Sonapur Ridge Corridor',
    timestamp: '09:50 IST',
    status: 'Cleared'
  }
];

export const DispatchCommandWorkspace: React.FC<DispatchCommandWorkspaceProps> = ({
  onBackToDashboard,
  onNavigateToSOP
}) => {
  // Threat Level State
  const [threatLevel, setThreatLevel] = useState<'LEVEL 1' | 'LEVEL 2' | 'LEVEL 3'>('LEVEL 3');

  // Card 1: SOP Sign-Off State
  const [isDigitalSigned, setIsDigitalSigned] = useState<boolean>(true);
  const [officerName, setOfficerName] = useState<string>('Dr. L. Thanmawia, IAS (DDMA Nodal Officer)');

  // Card 2: Broadcast Console State
  const [smsChannel, setSmsChannel] = useState<boolean>(true);
  const [whatsappChannel, setWhatsappChannel] = useState<boolean>(true);
  const [sirenChannel, setSirenChannel] = useState<boolean>(true);
  const [audience, setAudience] = useState<'All Corridor Users' | 'Local Residents (Geofenced)' | 'Tourists / Travelers'>('All Corridor Users');
  const [broadcastMessage, setBroadcastMessage] = useState<string>(
    'EMERGENCY ALERT (SDMA / DDMA): NH-6 Sonapur Corridor severed due to Level 3 Landslide. Mandatory evacuation ordered for Hunthar Veng & Zone 4. Detour via SH-12 bypass.'
  );
  
  // Tasks State
  const [tasks, setTasks] = useState<DispatchTask[]>(initialDispatchTasks);

  // Live isolated villages count from backend
  const [liveIsolatedCount, setLiveIsolatedCount] = useState<number | null>(null);

  const fetchIsolatedVillages = useCallback(async () => {
    try {
      const villages = await getIsolatedVillages();
      setLiveIsolatedCount(villages.length);
    } catch {
      // backend offline
    }
  }, []);

  useEffect(() => {
    fetchIsolatedVillages();
    const id = setInterval(fetchIsolatedVillages, 30_000);
    return () => clearInterval(id);
  }, [fetchIsolatedVillages]);


  // Security Confirmation Modal State
  const [isBroadcastModalOpen, setIsBroadcastModalOpen] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  const handleAddTask = (newTask: DispatchTask) => {
    setTasks(prev => [newTask, ...prev]);
    showToast(`Task ${newTask.id} assigned to ${newTask.agency} successfully!`);
  };

  const handleUpdateTaskStatus = (id: string, status: DispatchTask['status']) => {
    setTasks(tasks.map(t => t.id === id ? { ...t, status } : t));
    showToast(`Task ${id} status updated to ${status}.`);
  };

  const handleAuthorizeBroadcastSubmit = () => {
    setIsBroadcastModalOpen(false);
    showToast('🚨 EMERGENCY PUBLIC BROADCAST TRANSMITTED across SMS, WhatsApp & Siren Towers!');
  };

  const handleSOPRedirect = () => {
    if (!isDigitalSigned) {
      showToast('Please check the statutory certification box first.');
      return;
    }
    showToast('Dynamic SOP Administrative Order authorized and loaded.');
    if (onNavigateToSOP) {
      onNavigateToSOP();
    }
  };

  return (
    <div className="min-h-screen bg-slate-900/10 p-3 sm:p-6 space-y-4 font-sans">
      
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-20 right-6 z-[9999] flex items-center gap-3 bg-emerald-600 text-white px-5 py-3 rounded-2xl shadow-2xl backdrop-blur-md animate-bounce border border-white/20">
          <CheckCircle2 className="w-5 h-5 text-emerald-200 shrink-0" />
          <span className="text-sm font-semibold">{toastMessage}</span>
          <button onClick={() => setToastMessage(null)} className="ml-2 hover:bg-emerald-700 p-1 rounded-full">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Header Banner & High-Visibility Threat Level Switcher */}
      <div className="glass-panel-light rounded-3xl p-4 sm:p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-4 border border-white/80 shadow-xl">
        
        <div className="flex items-center gap-3">
          {onBackToDashboard && (
            <button 
              onClick={onBackToDashboard}
              className="p-2.5 rounded-2xl bg-white/80 hover:bg-emerald-50 text-slate-700 hover:text-[#10b981] transition-all border border-slate-200 shadow-sm flex items-center gap-2 group cursor-pointer"
            >
              <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
              <span className="text-xs font-bold hidden sm:inline">Dashboard</span>
            </button>
          )}

          <div className="w-10 h-10 rounded-2xl bg-rose-600 text-white flex items-center justify-center shadow-lg shadow-rose-500/30 shrink-0">
            <ShieldAlert className="w-6 h-6" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg sm:text-xl font-black text-slate-900 tracking-tight">
                DDMA Executive Dispatch Desk
              </h1>
              <span className="bg-slate-900 text-emerald-400 text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full border border-slate-700">
                Statutory Command Center
              </span>
            </div>
            <p className="text-xs text-slate-600 font-medium">
              Disaster Management Act 2005 Sec. 34 Statutory Dispatch &amp; Mass Public Warning Authorization
            </p>
          </div>
        </div>

        {/* HIGH-VISIBILITY THREAT LEVEL SWITCHER */}
        <div className="flex items-center gap-2 bg-slate-200/90 p-1.5 rounded-2xl border border-slate-300 shadow-inner">
          <span className="text-[10px] font-bold text-slate-500 uppercase px-2 hidden sm:inline">Threat Level:</span>
          
          <button
            onClick={() => setThreatLevel('LEVEL 1')}
            className={`px-3 py-1.5 rounded-xl text-xs font-black transition-all cursor-pointer ${
              threatLevel === 'LEVEL 1'
                ? 'bg-amber-500 text-white shadow-md'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            LEVEL 1 (ALERT)
          </button>

          <button
            onClick={() => setThreatLevel('LEVEL 2')}
            className={`px-3 py-1.5 rounded-xl text-xs font-black transition-all cursor-pointer ${
              threatLevel === 'LEVEL 2'
                ? 'bg-orange-600 text-white shadow-md'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            LEVEL 2 (EVACUATE)
          </button>

          <button
            onClick={() => setThreatLevel('LEVEL 3')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-black transition-all cursor-pointer flex items-center gap-1.5 ${
              threatLevel === 'LEVEL 3'
                ? 'bg-rose-600 text-white shadow-lg shadow-rose-600/40 ring-2 ring-rose-400 animate-pulse'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Zap className="w-3.5 h-3.5 fill-white" />
            <span>LEVEL 3 (CRITICAL RED)</span>
          </button>
        </div>

      </div>

      {/* Primary 3-Card Operational Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* CARD 1 (Left / lg:col-span-4): Statutory SOP Order Generator & Sign-Off */}
        <div className="lg:col-span-4 glass-panel-light rounded-3xl p-5 flex flex-col justify-between h-[720px] border border-white/80 shadow-xl space-y-4">
          <div className="space-y-4">
            
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-slate-900 text-emerald-400 flex items-center justify-center font-bold">
                  <FileText className="w-4 h-4 text-[#10b981]" />
                </div>
                <div>
                  <h3 className="text-sm font-black text-slate-900 tracking-tight">
                    Statutory SOP Order Authorization
                  </h3>
                  <p className="text-[10px] text-slate-500 font-mono">
                    Disaster Management Order Generator
                  </p>
                </div>
              </div>

              <span className="bg-emerald-100 text-[#10b981] border border-emerald-300 font-black text-[10px] px-2.5 py-0.5 rounded-full">
                Legal Valid
              </span>
            </div>

            {/* Live Summary Metrics */}
            <div className="grid grid-cols-3 gap-2 bg-slate-100/90 p-3 rounded-2xl border border-slate-200 text-center">
              <div>
                <span className="text-[10px] font-bold text-slate-500 block uppercase">Sector</span>
                <span className="text-xs font-black text-slate-900">NH-6 Cut</span>
              </div>

              <div>
                <span className="text-[10px] font-bold text-slate-500 block uppercase">Isolated Pop.</span>
                <span className="text-xs font-black text-rose-600">12,450</span>
              </div>

              <div>
                <span className="text-[10px] font-bold text-slate-500 block uppercase">Risk Score</span>
                <span className="text-xs font-black text-amber-600">87%</span>
              </div>
            </div>

            {/* Order Generator Box */}
            <div className="p-3.5 rounded-2xl bg-white border border-slate-200 space-y-2 text-xs">
              <div className="flex justify-between items-center text-slate-700 font-bold">
                <span>Order Reference Number</span>
                <span className="font-mono text-emerald-700">SDMA/NER/2026/SL-087</span>
              </div>
              <div className="flex justify-between items-center text-slate-700 font-bold">
                <span>Issuing Authority</span>
                <span className="font-mono text-slate-900">State DM Authority</span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-[11px] font-medium text-slate-700">
                "Issued under Sec. 34 of DMA 2005 for immediate traffic suspension on NH-6 Sonapur Corridor and mobilization of BRO 763 BRTF units."
              </div>
            </div>

            {/* Digital Signature Approval Box */}
            <div className="p-3.5 rounded-2xl bg-emerald-50/80 border border-emerald-200 space-y-3">
              <div className="flex items-center gap-2">
                <FileCheck2 className="w-4 h-4 text-[#10b981]" />
                <span className="text-xs font-extrabold text-slate-900">Officer Seal &amp; Certification</span>
              </div>

              <div className="space-y-1">
                <label className="block text-[10px] font-bold text-slate-600">Signing Nodal Officer</label>
                <input
                  type="text"
                  value={officerName}
                  onChange={(e) => setOfficerName(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded-xl px-2.5 py-1.5 text-xs font-bold text-slate-900"
                />
              </div>

              <label className="flex items-start gap-2 cursor-pointer pt-1">
                <input
                  type="checkbox"
                  checked={isDigitalSigned}
                  onChange={(e) => setIsDigitalSigned(e.target.checked)}
                  className="mt-0.5 accent-[#10b981]"
                />
                <span className="text-[11px] font-semibold text-slate-800 leading-snug">
                  I hereby certify statutory authorization under Disaster Management Act Sec. 34 and apply digital seal.
                </span>
              </label>
            </div>

          </div>

          {/* Action Buttons: Generate Order & Apply Officer Seal */}
          <div className="space-y-2">
            <button
              onClick={handleSOPRedirect}
              className="w-full py-2.5 rounded-xl bg-[#10b981] hover:bg-emerald-600 text-white font-extrabold text-xs shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95"
            >
              <FileText className="w-4 h-4" />
              <span>Generate &amp; Authorize Emergency Dispatch Order</span>
            </button>

            <button
              onClick={handleSOPRedirect}
              className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-emerald-400 font-extrabold text-xs shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95 border border-slate-700"
            >
              <FileCheck2 className="w-4 h-4 text-[#10b981]" />
              <span>Apply Officer Seal &amp; Publish Order</span>
            </button>
          </div>
        </div>

        {/* CARD 2 (Center / lg:col-span-4): Mass Public Warning Broadcast Console */}
        <div className="lg:col-span-4 glass-panel-light rounded-3xl p-5 flex flex-col justify-between h-[720px] border border-white/80 shadow-xl space-y-4">
          <div className="space-y-4">
            
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-slate-900 text-rose-400 flex items-center justify-center font-bold">
                  <Radio className="w-4 h-4 text-rose-500 animate-pulse" />
                </div>
                <div>
                  <h3 className="text-sm font-black text-slate-900 tracking-tight">
                    Mass Emergency Public Warning
                  </h3>
                  <p className="text-[10px] text-slate-500 font-mono">
                    Multi-Channel Broadcast Console
                  </p>
                </div>
              </div>

              <span className="bg-rose-100 text-rose-800 border border-rose-300 font-black text-[10px] px-2.5 py-0.5 rounded-full">
                Broadcast Ready
              </span>
            </div>

            {/* Multi-Channel Checkbox Selector */}
            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-slate-700">Transmission Channels</label>
              <div className="grid grid-cols-3 gap-2">
                
                <label className={`p-2.5 rounded-2xl border flex items-center gap-2 cursor-pointer text-xs font-bold transition-all ${
                  smsChannel ? 'bg-emerald-50 border-[#10b981] text-emerald-900 shadow-sm' : 'bg-slate-50 border-slate-200 text-slate-600'
                }`}>
                  <input
                    type="checkbox"
                    checked={smsChannel}
                    onChange={(e) => setSmsChannel(e.target.checked)}
                    className="accent-[#10b981]"
                  />
                  <Smartphone className="w-3.5 h-3.5 text-[#10b981]" />
                  <span>Mass SMS</span>
                </label>

                <label className={`p-2.5 rounded-2xl border flex items-center gap-2 cursor-pointer text-xs font-bold transition-all ${
                  whatsappChannel ? 'bg-emerald-50 border-[#10b981] text-emerald-900 shadow-sm' : 'bg-slate-50 border-slate-200 text-slate-600'
                }`}>
                  <input
                    type="checkbox"
                    checked={whatsappChannel}
                    onChange={(e) => setWhatsappChannel(e.target.checked)}
                    className="accent-[#10b981]"
                  />
                  <MessageSquare className="w-3.5 h-3.5 text-[#10b981]" />
                  <span>WhatsApp</span>
                </label>

                <label className={`p-2.5 rounded-2xl border flex items-center gap-2 cursor-pointer text-xs font-bold transition-all ${
                  sirenChannel ? 'bg-emerald-50 border-[#10b981] text-emerald-900 shadow-sm' : 'bg-slate-50 border-slate-200 text-slate-600'
                }`}>
                  <input
                    type="checkbox"
                    checked={sirenChannel}
                    onChange={(e) => setSirenChannel(e.target.checked)}
                    className="accent-[#10b981]"
                  />
                  <Volume2 className="w-3.5 h-3.5 text-[#10b981]" />
                  <span>Field Siren</span>
                </label>

              </div>
            </div>

            {/* Audience Segment Selector */}
            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-slate-700">Audience Target Segment</label>
              <select
                value={audience}
                onChange={(e) => setAudience(e.target.value as any)}
                className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] rounded-xl px-3 py-2 text-xs font-bold text-slate-900"
              >
                <option value="All Corridor Users">All Corridor Users (12,450 Population)</option>
                <option value="Local Residents (Geofenced)">Local Residents (Geofenced Sector)</option>
                <option value="Tourists / Travelers">Tourists &amp; Highway Travelers Only</option>
              </select>
            </div>

            {/* Editable Broadcast Message Textbox */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs font-bold text-slate-700">
                <span>Broadcast Alert Content</span>
                <span className="text-[10px] text-slate-400 font-mono">{broadcastMessage.length} chars</span>
              </div>
              <textarea
                rows={4}
                value={broadcastMessage}
                onChange={(e) => setBroadcastMessage(e.target.value)}
                className="w-full bg-white border border-slate-300 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20 rounded-2xl p-3 text-xs font-medium text-slate-800 leading-relaxed shadow-sm"
              />
            </div>

          </div>

          {/* Action Button: Authorize Broadcast */}
          <button
            onClick={() => setIsBroadcastModalOpen(true)}
            className="w-full py-3.5 rounded-2xl bg-rose-600 hover:bg-rose-700 text-white font-black text-xs shadow-lg shadow-rose-600/30 transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95"
          >
            <Radio className="w-4 h-4 animate-pulse" />
            <span>AUTHORIZE &amp; BROADCAST EMERGENCY ALERT</span>
          </button>
        </div>

        {/* CARD 3 (Right / lg:col-span-4): Inter-Agency Task Allocation Grid */}
        <div className="lg:col-span-4 h-[720px]">
          <ExecutiveDispatchPanel 
            tasks={tasks}
            onAddTask={handleAddTask}
            onUpdateTaskStatus={handleUpdateTaskStatus}
          />
        </div>

      </div>

      {/* MASS BROADCAST SECURITY CONFIRMATION MODAL */}
      {isBroadcastModalOpen && (
        <div className="fixed inset-0 z-[1200] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl border border-slate-200 animate-in zoom-in-95 duration-150 space-y-4">
            
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-rose-600" />
                <h3 className="text-sm font-extrabold text-slate-900">
                  Confirm Mass Emergency Broadcast
                </h3>
              </div>
              <button 
                onClick={() => setIsBroadcastModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 p-1 rounded-full"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-900 text-xs font-semibold space-y-2">
              <div className="font-extrabold flex items-center gap-1 text-rose-700">
                <ShieldAlert className="w-4 h-4" />
                <span>Statutory High-Impact Action</span>
              </div>
              <p className="text-[11px] text-rose-800 font-normal leading-relaxed">
                You are about to transmit a high-priority Emergency Alert to <strong>{audience}</strong> under Threat Level <strong>{threatLevel}</strong>.
              </p>
            </div>

            {/* Recipient breakdown */}
            <div className="bg-slate-100 p-3 rounded-2xl space-y-1.5 text-xs font-mono">
              <div className="flex justify-between">
                <span>Mass SMS Recipients:</span>
                <strong className="text-slate-900">{smsChannel ? '12,450' : 'Disabled'}</strong>
              </div>
              <div className="flex justify-between">
                <span>WhatsApp API Push:</span>
                <strong className="text-slate-900">{whatsappChannel ? '8,920' : 'Disabled'}</strong>
              </div>
              <div className="flex justify-between">
                <span>Field Siren Towers:</span>
                <strong className="text-slate-900">{sirenChannel ? '4 Active Towers' : 'Disabled'}</strong>
              </div>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <button
                onClick={() => setIsBroadcastModalOpen(false)}
                className="w-1/2 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-100 transition-all cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleAuthorizeBroadcastSubmit}
                className="w-1/2 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-extrabold text-xs shadow-md transition-all cursor-pointer"
              >
                Confirm &amp; Launch Broadcast
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
