import React, { useState } from 'react';
import { 
  Users, 
  Plus, 
  Send, 
  MapPin, 
  CheckCircle2, 
  Truck, 
  Radio, 
  UserCheck
} from 'lucide-react';
import type { DispatchTask } from '../types/dashboard';

interface ExecutiveDispatchPanelProps {
  tasks: DispatchTask[];
  onAddTask: (newTask: DispatchTask) => void;
  onUpdateTaskStatus: (id: string, status: DispatchTask['status']) => void;
}

export const ExecutiveDispatchPanel: React.FC<ExecutiveDispatchPanelProps> = ({
  tasks,
  onAddTask,
  onUpdateTaskStatus
}) => {
  // Form State
  const [agency, setAgency] = useState<DispatchTask['agency']>('BRO');
  const [taskName, setTaskName] = useState<string>('Heavy Debris Clearing & Barrier Deployment');
  const [commanderName, setCommanderName] = useState<string>('Col. R. Sharma, BRO 763 BRTF');
  const [priority, setPriority] = useState<DispatchTask['priority']>('Urgent');
  const [targetSector, setTargetSector] = useState<string>('NH-6 Sonapur Cut');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskName.trim()) return;

    const newTask: DispatchTask = {
      id: `TASK-${Date.now().toString().slice(-4)}`,
      agency,
      taskName,
      commanderName,
      priority,
      targetSector,
      timestamp: `${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })} IST`,
      status: 'En Route'
    };

    onAddTask(newTask);
    setTaskName('');
  };

  const getAgencyBadge = (agencyName: DispatchTask['agency']) => {
    switch (agencyName) {
      case 'BRO':
        return <span className="bg-amber-100 text-amber-900 border border-amber-300 font-extrabold text-[10px] px-2 py-0.5 rounded-full">BRO (Border Roads)</span>;
      case 'NDRF':
        return <span className="bg-emerald-100 text-emerald-900 border border-emerald-300 font-extrabold text-[10px] px-2 py-0.5 rounded-full">NDRF Response</span>;
      case 'SDRF':
        return <span className="bg-cyan-100 text-cyan-900 border border-cyan-300 font-extrabold text-[10px] px-2 py-0.5 rounded-full">SDRF State</span>;
      case 'IAF Cell':
        return <span className="bg-purple-100 text-purple-900 border border-purple-300 font-extrabold text-[10px] px-2 py-0.5 rounded-full">IAF Helicopter Airlift</span>;
      default:
        return <span className="bg-slate-100 text-slate-800 border border-slate-300 font-extrabold text-[10px] px-2 py-0.5 rounded-full">District Police</span>;
    }
  };

  const getStatusPill = (status: DispatchTask['status']) => {
    switch (status) {
      case 'On-Site Ops Active':
        return (
          <span className="bg-emerald-600 text-white font-extrabold text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1 shadow-sm">
            <Radio className="w-2.5 h-2.5 animate-pulse" />
            <span>On-Site Ops Active</span>
          </span>
        );
      case 'En Route':
        return (
          <span className="bg-amber-500 text-white font-extrabold text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1">
            <Truck className="w-2.5 h-2.5" />
            <span>En Route</span>
          </span>
        );
      case 'Cleared':
        return (
          <span className="bg-slate-200 text-slate-700 font-extrabold text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1">
            <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" />
            <span>Cleared</span>
          </span>
        );
    }
  };

  return (
    <div className="glass-panel-light rounded-3xl p-5 border border-white/90 shadow-xl flex flex-col justify-between gap-4 h-full overflow-y-auto">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-slate-900 text-emerald-400 flex items-center justify-center font-bold">
            <Users className="w-4 h-4 text-[#10b981]" />
          </div>
          <div>
            <h3 className="text-sm font-black text-slate-900 tracking-tight">
              Inter-Agency Task Allocation Matrix
            </h3>
            <p className="text-[10px] text-slate-500 font-mono">
              Multi-Agency Field Operational Dispatch
            </p>
          </div>
        </div>

        <span className="bg-slate-100 text-slate-700 font-mono text-[10px] font-bold px-2.5 py-1 rounded-full border border-slate-200">
          {tasks.length} Active Tasks
        </span>
      </div>

      {/* Task Creation Form */}
      <form onSubmit={handleSubmit} className="p-3.5 rounded-2xl bg-white/70 border border-slate-200/80 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-extrabold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
            <Plus className="w-4 h-4 text-[#10b981]" />
            <span>Create New Field Deployment Task</span>
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2.5">
          {/* Agency Selector */}
          <div>
            <label className="block text-[10px] font-bold text-slate-600 mb-1">Target Agency</label>
            <select
              value={agency}
              onChange={(e) => setAgency(e.target.value as any)}
              className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] rounded-xl px-2.5 py-1.5 text-xs font-bold text-slate-900"
            >
              <option value="BRO">BRO (Border Roads Org)</option>
              <option value="NDRF">NDRF (National Response)</option>
              <option value="SDRF">SDRF (State Response)</option>
              <option value="District Police">District Police</option>
              <option value="IAF Cell">IAF Helicopter Cell</option>
            </select>
          </div>

          {/* Priority Selector */}
          <div>
            <label className="block text-[10px] font-bold text-slate-600 mb-1">Priority Level</label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as any)}
              className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] rounded-xl px-2.5 py-1.5 text-xs font-bold text-slate-900"
            >
              <option value="Urgent">🔴 Urgent (Immediate Action)</option>
              <option value="Standard">🟡 Standard (Operational Support)</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2.5">
          {/* Target Sector Selector */}
          <div>
            <label className="block text-[10px] font-bold text-slate-600 mb-1">Target Sector</label>
            <select
              value={targetSector}
              onChange={(e) => setTargetSector(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] rounded-xl px-2.5 py-1.5 text-xs font-semibold text-slate-900"
            >
              <option value="NH-6 Sonapur Cut">NH-6 Sonapur Cut</option>
              <option value="Hunthar Veng Slope">Hunthar Veng Slope</option>
              <option value="Kolasib Sector">Kolasib Sector</option>
              <option value="Aizawl Bypass">Aizawl Bypass</option>
            </select>
          </div>

          {/* Commander Name */}
          <div>
            <label className="block text-[10px] font-bold text-slate-600 mb-1">Assigned Commander</label>
            <input
              type="text"
              value={commanderName}
              onChange={(e) => setCommanderName(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] rounded-xl px-2.5 py-1.5 text-xs font-semibold text-slate-900"
              placeholder="Commander Name & Unit"
            />
          </div>
        </div>

        {/* Task Name Input */}
        <div>
          <label className="block text-[10px] font-bold text-slate-600 mb-1">Task Specification</label>
          <input
            type="text"
            value={taskName}
            onChange={(e) => setTaskName(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] rounded-xl px-2.5 py-1.5 text-xs font-semibold text-slate-900"
            placeholder="e.g. Deploy Heavy Earthmover & Debris Clearing Unit"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-[#10b981] hover:bg-emerald-600 text-white font-extrabold text-xs py-2 rounded-xl shadow transition-all flex items-center justify-center gap-1.5 cursor-pointer"
        >
          <Send className="w-3.5 h-3.5" />
          <span>Assign &amp; Deploy Task</span>
        </button>
      </form>

      {/* Active Duty List */}
      <div className="space-y-2 flex-1 overflow-y-auto max-h-[280px] pr-1">
        <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider block mb-1">
          Active Duty Deployments
        </span>

        {tasks.map((task) => (
          <div 
            key={task.id}
            className="p-3 rounded-2xl bg-white border border-slate-200/90 shadow-sm space-y-2 text-xs hover:border-emerald-300 transition-colors"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                {getAgencyBadge(task.agency)}
                <span className="font-mono font-black text-slate-900 text-[11px]">
                  {task.id}
                </span>
              </div>

              {getStatusPill(task.status)}
            </div>

            <div className="font-bold text-slate-900 text-xs">
              {task.taskName}
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2 text-[10px] font-medium text-slate-500 pt-1 border-t border-slate-100">
              <div className="flex items-center gap-1">
                <UserCheck className="w-3 h-3 text-[#10b981]" />
                <span className="font-semibold text-slate-800">{task.commanderName}</span>
              </div>

              <div className="flex items-center gap-2">
                <span className="flex items-center gap-0.5 text-slate-600 font-mono">
                  <MapPin className="w-3 h-3 text-slate-400" />
                  {task.targetSector}
                </span>
                
                {/* Status Toggle Selector */}
                <select
                  value={task.status}
                  onChange={(e) => onUpdateTaskStatus(task.id, e.target.value as any)}
                  className="bg-slate-100 border border-slate-300 rounded px-1.5 py-0.5 text-[10px] font-bold text-slate-800"
                >
                  <option value="En Route">En Route</option>
                  <option value="On-Site Ops Active">On-Site Ops Active</option>
                  <option value="Cleared">Cleared</option>
                </select>
              </div>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
};
