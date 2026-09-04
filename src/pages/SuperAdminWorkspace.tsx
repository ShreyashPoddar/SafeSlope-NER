import React, { useState } from 'react';
import { 
  ShieldCheck, 
  ArrowLeft, 
  Users, 
  Key, 
  FileText, 
  Search, 
  Download, 
  CheckCircle2, 
  X, 
  AlertTriangle, 
  UserPlus, 
  Activity, 
  UserX, 
  RotateCcw
} from 'lucide-react';
import { AdminSystemPanel } from '../components/AdminSystemPanel';
import type { UserAccount, SystemLog, UserProfile } from '../types/dashboard';

interface SuperAdminWorkspaceProps {
  currentUser?: UserProfile | null;
  onBackToDashboard?: () => void;
}

// Initial Mock User Accounts for RBAC Directory
const initialUserAccounts: UserAccount[] = [
  {
    id: 'USR-101',
    name: 'Dr. L. Thanmawia, IAS',
    contact: 'thanmawia.ias@gov.in',
    category: 'Admin',
    role: 'Emergency Dispatch & DDMA Nodal Officer',
    status: 'Active',
    lastLogin: '10 mins ago'
  },
  {
    id: 'USR-102',
    name: 'Er. Joseph Lalrinliana',
    contact: '+91 98625 44102',
    category: 'Admin',
    role: 'Geotechnical & Meteorological Officer',
    status: 'Active',
    lastLogin: '25 mins ago'
  },
  {
    id: 'USR-103',
    name: 'C. Zothantluanga',
    contact: '+91 94361 77190',
    category: 'Admin',
    role: 'Incident Moderation & Citizen Report Admin',
    status: 'Active',
    lastLogin: '1 hour ago'
  },
  {
    id: 'USR-104',
    name: 'Capt. R. K. Sailo',
    contact: '+91 98620 11982',
    category: 'Admin',
    role: 'First Responder / Field Operations Officer',
    status: 'Active',
    lastLogin: '3 hours ago'
  },
  {
    id: 'USR-105',
    name: 'Lalthanzama Fanai',
    contact: '+91 94361 99201',
    category: 'User',
    role: 'Local Resident',
    status: 'Active',
    lastLogin: 'Yesterday'
  },
  {
    id: 'USR-106',
    name: 'Rohan Sharma',
    contact: 'rohan.sharma@gmail.com',
    category: 'User',
    role: 'Tourist / Traveler',
    status: 'Suspended',
    lastLogin: '3 days ago'
  }
];

// Initial Mock System Security Logs
const initialSystemLogs: SystemLog[] = [
  {
    id: 'LOG-8801',
    timestamp: '2026-09-04 10:18:24 IST',
    actor: 'Dr. L. Thanmawia (USR-101)',
    actorRole: 'DDMA Nodal Officer',
    action: 'SOP Dispatch Order Authorized (SDMA/NER/2026/SL-087)',
    zone: 'Zone 4',
    ipAddress: '10.14.22 font-mono',
    severity: 'Critical Security Event'
  },
  {
    id: 'LOG-8802',
    timestamp: '2026-09-04 10:04:12 IST',
    actor: 'Er. Joseph Lalrinliana (USR-102)',
    actorRole: 'Geotech Specialist',
    action: 'Telemetry Override engaged: Rainfall 42.5mm/h',
    zone: 'Zone 1',
    ipAddress: '10.14.18.9',
    severity: 'Warning'
  },
  {
    id: 'LOG-8803',
    timestamp: '2026-09-04 09:55:08 IST',
    actor: 'Er. Joseph Lalrinliana (USR-102)',
    actorRole: 'Geotech Specialist',
    action: 'Polygon Edit: NH-6 Milepost 44 Landslide Polygon severity updated to Level 2',
    zone: 'Zone 1',
    ipAddress: '10.14.18.9',
    severity: 'Info'
  },
  {
    id: 'LOG-8804',
    timestamp: '2026-09-04 09:36:45 IST',
    actor: 'C. Zothantluanga (USR-103)',
    actorRole: 'Incident Moderation Admin',
    action: 'Approved & Published Citizen Report INC-2026-SL087',
    zone: 'Zone 4',
    ipAddress: '10.14.20.12',
    severity: 'Info'
  }
];

export const SuperAdminWorkspace: React.FC<SuperAdminWorkspaceProps> = ({ 
  currentUser,
  onBackToDashboard
}) => {
  // Tab State: 'users' | 'vault' | 'logs'
  const [activeTab, setActiveTab] = useState<'users' | 'vault' | 'logs'>('users');
  
  // Toast State
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  
  // User Accounts State (Tab 1)
  const [users, setUsers] = useState<UserAccount[]>(initialUserAccounts);
  const [userSearch, setUserSearch] = useState<string>('');
  const [isProvisionModalOpen, setIsProvisionModalOpen] = useState<boolean>(false);

  // New Admin Account Form State
  const [newAdminName, setNewAdminName] = useState<string>('');
  const [newAdminContact, setNewAdminContact] = useState<string>('');
  const [newAdminRole, setNewAdminRole] = useState<string>('Geotechnical & Meteorological Officer');

  // Logs State (Tab 3)
  const [logs] = useState<SystemLog[]>(initialSystemLogs);
  const [zoneFilter, setZoneFilter] = useState<string>('All');
  const [actionFilter, setActionFilter] = useState<string>('All');

  const isHeadAdmin = currentUser?.persona === 'head_admin' || currentUser?.portalType === 'admin';

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Provision New Admin Submit
  const handleProvisionSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAdminName.trim() || !newAdminContact.trim()) return;

    const created: UserAccount = {
      id: `USR-${Date.now().toString().slice(-3)}`,
      name: newAdminName,
      contact: newAdminContact,
      category: 'Admin',
      role: newAdminRole,
      status: 'Active',
      lastLogin: 'Just now'
    };

    setUsers([created, ...users]);
    setIsProvisionModalOpen(false);
    setNewAdminName('');
    setNewAdminContact('');
    showToast(`Provisioned new Admin account for ${created.name} (${created.role}).`);
  };

  // User Actions
  const handleSuspendUser = (id: string) => {
    setUsers(users.map(u => u.id === id ? { ...u, status: u.status === 'Active' ? 'Suspended' : 'Active' } : u));
    showToast(`Updated account status for user ${id}.`);
  };

  const handleResetCreds = (name: string) => {
    showToast(`Credential reset link sent to ${name}.`);
  };

  // Export Audit Logs
  const handleExportLogs = () => {
    showToast('Exporting System Security Audit Log (CSV/PDF)...');
  };

  // Filtered Users
  const filteredUsers = users.filter(u => 
    u.name.toLowerCase().includes(userSearch.toLowerCase()) ||
    u.contact.toLowerCase().includes(userSearch.toLowerCase()) ||
    u.role.toLowerCase().includes(userSearch.toLowerCase())
  );

  // Filtered Logs
  const filteredLogs = logs.filter(l => {
    const zoneMatch = zoneFilter === 'All' || l.zone === zoneFilter;
    const actionMatch = actionFilter === 'All' || l.action.toLowerCase().includes(actionFilter.toLowerCase());
    return zoneMatch && actionMatch;
  });

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

      {/* Security Gate Warning if non-Head Admin */}
      {!isHeadAdmin && (
        <div className="bg-rose-600 text-white p-4 rounded-3xl shadow-xl flex items-center gap-3 animate-pulse border border-white/30">
          <AlertTriangle className="w-6 h-6 text-yellow-300 shrink-0" />
          <div>
            <span className="font-extrabold text-sm uppercase block">⚠️ SECURE AUTHORIZATION GATE</span>
            <p className="text-xs font-medium">
              You are currently viewing the Head Admin Portal. Restricted to authorized Head Admin personnel under SDMA Security Guidelines.
            </p>
          </div>
        </div>
      )}

      {/* Header Banner & System Health Indicators */}
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

          <div className="w-10 h-10 rounded-2xl bg-slate-900 text-emerald-400 flex items-center justify-center shadow-lg shrink-0">
            <ShieldCheck className="w-6 h-6 text-[#10b981]" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg sm:text-xl font-black text-slate-900 tracking-tight">
                System &amp; Platform Control Center
              </h1>
              <span className="bg-slate-900 text-emerald-400 text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full border border-slate-700">
                Head Admin Portal
              </span>
            </div>
            <p className="text-xs text-slate-600 font-medium">
              Global Platform Governance, RBAC Directory, API Integration Vault &amp; System Audit
            </p>
          </div>
        </div>

        {/* System Health Indicators */}
        <div className="flex items-center gap-3">
          
          <div className="bg-emerald-50 border border-emerald-300 px-3.5 py-1.5 rounded-2xl flex items-center gap-2 shadow-sm">
            <Activity className="w-4 h-4 text-[#10b981] animate-pulse" />
            <div>
              <span className="text-[9px] font-extrabold text-emerald-900 block uppercase">System Health Status</span>
              <span className="text-xs font-black text-emerald-700">System Operational (100% Uptime)</span>
            </div>
          </div>

          <div className="bg-white/80 border border-slate-200 px-3.5 py-1.5 rounded-2xl flex items-center gap-2 shadow-sm">
            <Key className="w-4 h-4 text-emerald-600" />
            <div>
              <span className="text-[9px] font-extrabold text-slate-500 block uppercase">Integrations</span>
              <span className="text-xs font-black text-slate-900">Active Links: 4/4</span>
            </div>
          </div>

        </div>
      </div>

      {/* Tab Navigation Switcher */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab('users')}
          className={`px-4 py-2 rounded-2xl text-xs font-black transition-all cursor-pointer flex items-center gap-2 ${
            activeTab === 'users' 
              ? 'bg-[#10b981] text-white shadow-md' 
              : 'glass-panel-light text-slate-700 hover:bg-white'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>User &amp; RBAC Directory</span>
        </button>

        <button
          onClick={() => setActiveTab('vault')}
          className={`px-4 py-2 rounded-2xl text-xs font-black transition-all cursor-pointer flex items-center gap-2 ${
            activeTab === 'vault' 
              ? 'bg-[#10b981] text-white shadow-md' 
              : 'glass-panel-light text-slate-700 hover:bg-white'
          }`}
        >
          <Key className="w-4 h-4" />
          <span>API &amp; Integration Vault</span>
        </button>

        <button
          onClick={() => setActiveTab('logs')}
          className={`px-4 py-2 rounded-2xl text-xs font-black transition-all cursor-pointer flex items-center gap-2 ${
            activeTab === 'logs' 
              ? 'bg-[#10b981] text-white shadow-md' 
              : 'glass-panel-light text-slate-700 hover:bg-white'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Security Audit &amp; Logs</span>
        </button>
      </div>

      {/* TAB 1: User & RBAC Directory */}
      {activeTab === 'users' && (
        <div className="glass-panel-light rounded-3xl p-5 border border-white/80 shadow-xl space-y-4">
          
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-3">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search accounts by name, contact, or role..."
                value={userSearch}
                onChange={(e) => setUserSearch(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] rounded-xl pl-9 pr-3 py-1.5 text-xs font-semibold text-slate-800"
              />
            </div>

            <button
              onClick={() => setIsProvisionModalOpen(true)}
              className="bg-[#10b981] hover:bg-emerald-600 text-white font-extrabold text-xs px-4 py-2 rounded-xl shadow transition-all flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <UserPlus className="w-4 h-4" />
              <span>+ Provision New Admin Account</span>
            </button>
          </div>

          {/* User Directory Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 font-bold uppercase text-[10px]">
                  <th className="py-2.5 px-3">Name</th>
                  <th className="py-2.5 px-3">Contact</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Assigned Role</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Last Login</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {filteredUsers.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50/80 transition-colors text-slate-800">
                    <td className="py-3 px-3 font-bold text-slate-900 flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-slate-200 text-slate-800 font-bold flex items-center justify-center text-[10px]">
                        {u.name.slice(0, 2).toUpperCase()}
                      </div>
                      <span>{u.name}</span>
                    </td>
                    <td className="py-3 px-3 font-mono text-[11px] text-slate-600">{u.contact}</td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase ${
                        u.category === 'Admin' ? 'bg-slate-900 text-emerald-400' : 'bg-slate-100 text-slate-700'
                      }`}>
                        {u.category}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-bold text-slate-800">{u.role}</td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        u.status === 'Active' ? 'bg-emerald-100 text-emerald-900' : 'bg-rose-100 text-rose-900'
                      }`}>
                        {u.status}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-[11px] text-slate-500">{u.lastLogin}</td>
                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button 
                          onClick={() => handleResetCreds(u.name)}
                          title="Reset Credentials" 
                          className="p-1.5 rounded-lg hover:bg-slate-200 text-slate-600 transition-colors"
                        >
                          <RotateCcw className="w-3.5 h-3.5" />
                        </button>
                        <button 
                          onClick={() => handleSuspendUser(u.id)}
                          title="Suspend/Activate" 
                          className="p-1.5 rounded-lg hover:bg-rose-100 text-rose-600 transition-colors"
                        >
                          <UserX className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>
      )}

      {/* TAB 2: API & Integration Vault */}
      {activeTab === 'vault' && (
        <AdminSystemPanel onShowToast={showToast} />
      )}

      {/* TAB 3: Security Audit & Logs */}
      {activeTab === 'logs' && (
        <div className="glass-panel-light rounded-3xl p-5 border border-white/80 shadow-xl space-y-4">
          
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-3">
            
            {/* Filter Controls */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-bold text-slate-700">Filter Zone:</span>
                <select
                  value={zoneFilter}
                  onChange={(e) => setZoneFilter(e.target.value)}
                  className="bg-slate-50 border border-slate-300 rounded-xl px-2.5 py-1 text-xs font-bold text-slate-900"
                >
                  <option value="All">All Zones</option>
                  <option value="Zone 1">Zone 1 (GIS Map &amp; Sensors)</option>
                  <option value="Zone 2">Zone 2 (Telemetry &amp; Control)</option>
                  <option value="Zone 3">Zone 3 (Isolation Twin)</option>
                  <option value="Zone 4">Zone 4 (Incident Queue)</option>
                </select>
              </div>

              <div className="flex items-center gap-1.5">
                <span className="text-xs font-bold text-slate-700">Action Type:</span>
                <select
                  value={actionFilter}
                  onChange={(e) => setActionFilter(e.target.value)}
                  className="bg-slate-50 border border-slate-300 rounded-xl px-2.5 py-1 text-xs font-bold text-slate-900"
                >
                  <option value="All">All Actions</option>
                  <option value="SOP Dispatch">SOP Dispatch</option>
                  <option value="Telemetry Override">Telemetry Override</option>
                  <option value="Polygon Edit">Polygon Edit</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleExportLogs}
              className="bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-xs px-4 py-2 rounded-xl shadow transition-all flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <Download className="w-4 h-4 text-emerald-400" />
              <span>Export System Audit Log (CSV/PDF)</span>
            </button>
          </div>

          {/* High-Density Security Log Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 font-bold uppercase text-[10px]">
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Actor (ID &amp; Role)</th>
                  <th className="py-2.5 px-3">Action Description</th>
                  <th className="py-2.5 px-3">Zone</th>
                  <th className="py-2.5 px-3">IP Address</th>
                  <th className="py-2.5 px-3">Severity Level</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {filteredLogs.map((l) => (
                  <tr key={l.id} className="hover:bg-slate-50/80 transition-colors text-slate-800">
                    <td className="py-3 px-3 font-mono text-[11px] text-slate-500">{l.timestamp}</td>
                    <td className="py-3 px-3 font-bold text-slate-900">
                      <div>{l.actor}</div>
                      <div className="text-[10px] text-slate-400 font-normal">{l.actorRole}</div>
                    </td>
                    <td className="py-3 px-3 font-semibold text-slate-800">{l.action}</td>
                    <td className="py-3 px-3 font-bold text-slate-700">{l.zone}</td>
                    <td className="py-3 px-3 font-mono text-[11px] text-slate-500">{l.ipAddress}</td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase ${
                        l.severity === 'Critical Security Event'
                          ? 'bg-rose-100 text-rose-900 border border-rose-300'
                          : l.severity === 'Warning'
                          ? 'bg-amber-100 text-amber-900 border border-amber-300'
                          : 'bg-slate-100 text-slate-700'
                      }`}>
                        {l.severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>
      )}

      {/* PROVISION NEW ADMIN ACCOUNT MODAL */}
      {isProvisionModalOpen && (
        <div className="fixed inset-0 z-[1200] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl border border-slate-200 animate-in zoom-in-95 duration-150 space-y-4">
            
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center gap-2">
                <UserPlus className="w-5 h-5 text-[#10b981]" />
                <h3 className="text-sm font-extrabold text-slate-900">
                  Provision New Admin Personnel Account
                </h3>
              </div>
              <button 
                onClick={() => setIsProvisionModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 p-1 rounded-full"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleProvisionSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Personnel Full Name</label>
                <input
                  type="text"
                  required
                  value={newAdminName}
                  onChange={(e) => setNewAdminName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] rounded-xl px-3 py-2 text-xs font-semibold text-slate-900"
                  placeholder="e.g. Dr. A. K. Roy"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Official Email or Mobile Number</label>
                <input
                  type="text"
                  required
                  value={newAdminContact}
                  onChange={(e) => setNewAdminContact(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] rounded-xl px-3 py-2 text-xs font-semibold text-slate-900"
                  placeholder="name@gov.in or +91 98625 00000"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Assigned Operational Sub-Role</label>
                <select
                  value={newAdminRole}
                  onChange={(e) => setNewAdminRole(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 focus:border-[#10b981] rounded-xl px-3 py-2 text-xs font-bold text-slate-900"
                >
                  <option value="Geotechnical & Meteorological Officer">1. Geotechnical &amp; Meteorological Officer</option>
                  <option value="Incident Moderation & Citizen Report Admin">2. Incident Moderation &amp; Citizen Report Admin</option>
                  <option value="Emergency Dispatch & DDMA Nodal Officer">3. Emergency Dispatch &amp; DDMA Nodal Officer</option>
                  <option value="First Responder / Field Operations Officer">4. First Responder / Field Operations Officer</option>
                </select>
              </div>

              <div className="flex items-center gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setIsProvisionModalOpen(false)}
                  className="w-1/2 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-100 transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="w-1/2 py-2.5 rounded-xl bg-[#10b981] hover:bg-emerald-600 text-white font-extrabold text-xs shadow-md transition-all cursor-pointer"
                >
                  Provision Account
                </button>
              </div>
            </form>

          </div>
        </div>
      )}

    </div>
  );
};
