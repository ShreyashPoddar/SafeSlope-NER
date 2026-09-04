import React, { useState, useRef, useEffect } from 'react';
import { 
  User, 
  Activity, 
  LayoutDashboard, 
  Smartphone, 
  FileText, 
  LogOut, 
  UserPlus, 
  LogIn, 
  ShieldAlert, 
  Compass, 
  Bookmark, 
  FileCheck, 
  ChevronDown,
  Shield,
  Radio,
  Truck,
  Sliders,
  Sparkles
} from 'lucide-react';
import { DownloadSOPButton } from './SOPDocument';
import type { UserProfile, IsolationStats } from '../types/dashboard';

interface NavbarProps {
  currentPath: string;
  currentUser: UserProfile | null;
  isolationStats: IsolationStats;
  onNavigate: (path: string) => void;
  onOpenAuth: (isRegisterMode: boolean) => void;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentPath,
  currentUser,
  isolationStats,
  onNavigate,
  onOpenAuth,
  onLogout
}) => {
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState<boolean>(false);
  const [isAdminSwitcherOpen, setIsAdminSwitcherOpen] = useState<boolean>(false);
  
  const profileRef = useRef<HTMLDivElement>(null);
  const adminSwitcherRef = useRef<HTMLDivElement>(null);

  // Close dropdowns on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setIsProfileDropdownOpen(false);
      }
      if (adminSwitcherRef.current && !adminSwitcherRef.current.contains(event.target as Node)) {
        setIsAdminSwitcherOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const isHeadAdmin = currentUser?.persona === 'head_admin' || currentUser?.subRole === 'Head Admin';
  const isRoleAdmin = currentUser?.portalType === 'admin' && !isHeadAdmin;

  // Head Admin workspace options
  const adminWorkspaces = [
    { path: '/admin/geotech', name: 'Geotech & Met Officer', icon: Compass, badge: 'Zone 1' },
    { path: '/admin/moderation', name: 'Incident Moderation Desk', icon: ShieldAlert, badge: 'Zone 4' },
    { path: '/admin/dispatch', name: 'Executive Dispatch (DDMA)', icon: Radio, badge: 'Statutory' },
    { path: '/admin/field-ops', name: 'Field Operations Unit', icon: Truck, badge: 'Tactical' },
    { path: '/admin/system', name: 'System Control (Super Admin)', icon: Shield, badge: 'Super Admin' }
  ];

  return (
    <header className="flex flex-wrap items-center justify-between gap-4 py-1.5 px-1 relative z-[1100]">
      
      {/* 1. Left: Mountain/Slope Emblem + SafeSlope Title */}
      <div 
        onClick={() => onNavigate('/')}
        className="flex items-center gap-2.5 cursor-pointer group"
      >
        <div className="w-9 h-9 rounded-full bg-emerald-400/20 flex items-center justify-center text-emerald-300 group-hover:bg-emerald-400/30 transition-all">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="m8 3 4 8 5-5 15H2L8 3z"/>
          </svg>
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight font-sans drop-shadow-sm leading-none">
            SafeSlope
          </h1>
          <span className="text-[10px] text-emerald-300 font-mono font-semibold block mt-0.5">
            SDMA North East Region
          </span>
        </div>
      </div>

      {/* 2. Center: Live Status Pulse + View Navigation Buttons */}
      <div className="flex items-center gap-3">
        <div className="hidden lg:flex items-center gap-2 px-4 py-1.5 rounded-full glass-pill text-slate-800 text-xs font-semibold">
          <Activity className="w-4 h-4 text-[#10b981] animate-pulse" />
          <span>Live Status Pulse</span>
        </div>

        {/* Navigation Bar Pills */}
        <div className="flex items-center p-1 rounded-full glass-pill text-xs font-semibold gap-1">
          
          {/* Always Available Public Navigation Items */}
          <button
            onClick={() => onNavigate('/')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all cursor-pointer ${
              currentPath === '/' || currentPath === ''
                ? 'bg-[#10b981] text-white shadow-sm font-bold' 
                : 'text-slate-700 hover:text-slate-900 hover:bg-white/50'
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Command Grid</span>
          </button>
          
          <button
            onClick={() => onNavigate('/report')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all cursor-pointer ${
              currentPath === '/report' 
                ? 'bg-[#10b981] text-white shadow-sm font-bold' 
                : 'text-slate-700 hover:text-slate-900 hover:bg-white/50'
            }`}
          >
            <Smartphone className="w-3.5 h-3.5" />
            <span>Report Hazard</span>
          </button>

          <button
            onClick={() => onNavigate('/sop')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all cursor-pointer ${
              currentPath === '/sop' 
                ? 'bg-[#10b981] text-white shadow-sm font-bold' 
                : 'text-slate-700 hover:text-slate-900 hover:bg-white/50'
            }`}
          >
            <FileText className="w-3.5 h-3.5 text-emerald-700" />
            <span>SOP Order</span>
          </button>

          {/* Role-Based Admin: Only render link to assigned workspace */}
          {isRoleAdmin && (
            <>
              {currentUser.subRole?.includes('Geotechnical') && (
                <button
                  onClick={() => onNavigate('/admin/geotech')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all cursor-pointer ${
                    currentPath === '/admin/geotech'
                      ? 'bg-[#10b981] text-white shadow-sm font-bold' 
                      : 'text-slate-700 hover:text-slate-900 hover:bg-white/50'
                  }`}
                >
                  <Compass className="w-3.5 h-3.5 text-emerald-700" />
                  <span>Geotech Officer</span>
                </button>
              )}

              {(currentUser.subRole?.includes('Incident') || currentUser.subRole?.includes('Moderation')) && (
                <button
                  onClick={() => onNavigate('/admin/moderation')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all cursor-pointer ${
                    currentPath === '/admin/moderation'
                      ? 'bg-[#10b981] text-white shadow-sm font-bold' 
                      : 'text-slate-700 hover:text-slate-900 hover:bg-white/50'
                  }`}
                >
                  <ShieldAlert className="w-3.5 h-3.5 text-emerald-700" />
                  <span>Moderation Desk</span>
                </button>
              )}

              {(currentUser.subRole?.includes('Dispatch') || currentUser.subRole?.includes('DDMA')) && (
                <button
                  onClick={() => onNavigate('/admin/dispatch')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all cursor-pointer ${
                    currentPath === '/admin/dispatch'
                      ? 'bg-[#10b981] text-white shadow-sm font-bold' 
                      : 'text-slate-700 hover:text-slate-900 hover:bg-white/50'
                  }`}
                >
                  <Radio className="w-3.5 h-3.5 text-emerald-700 animate-pulse" />
                  <span>Executive Dispatch</span>
                </button>
              )}

              {(currentUser.subRole?.includes('First Responder') || currentUser.subRole?.includes('Field')) && (
                <button
                  onClick={() => onNavigate('/admin/field-ops')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all cursor-pointer ${
                    currentPath === '/admin/field-ops'
                      ? 'bg-[#10b981] text-white shadow-sm font-bold' 
                      : 'text-slate-700 hover:text-slate-900 hover:bg-white/50'
                  }`}
                >
                  <Truck className="w-3.5 h-3.5 text-emerald-700" />
                  <span>Field Ops</span>
                </button>
              )}
            </>
          )}

          {/* Head Admin: Render Head Admin Switcher Dropdown */}
          {isHeadAdmin && (
            <div className="relative" ref={adminSwitcherRef}>
              <button
                onClick={() => setIsAdminSwitcherOpen(!isAdminSwitcherOpen)}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full transition-all cursor-pointer font-bold ${
                  currentPath.startsWith('/admin')
                    ? 'bg-slate-900 text-emerald-400 shadow-md border border-slate-700' 
                    : 'bg-white/70 text-slate-800 hover:bg-white border border-slate-300/60'
                }`}
              >
                <Sliders className="w-3.5 h-3.5 text-emerald-400" />
                <span>Head Admin Switcher</span>
                <ChevronDown className={`w-3 h-3 transition-transform ${isAdminSwitcherOpen ? 'rotate-180' : ''}`} />
              </button>

              {isAdminSwitcherOpen && (
                <div className="absolute top-11 left-0 w-64 bg-slate-900/95 backdrop-blur-xl border border-slate-700/80 shadow-2xl rounded-2xl p-2 text-white animate-in fade-in slide-in-from-top-2 duration-150 z-[1200]">
                  <div className="px-3 py-2 border-b border-slate-800 flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                      <Sparkles className="w-3 h-3 text-emerald-400" />
                      Head Admin Privileges Active
                    </span>
                  </div>

                  <div className="mt-1 space-y-0.5">
                    {adminWorkspaces.map((ws) => {
                      const Icon = ws.icon;
                      const isActive = currentPath === ws.path;
                      return (
                        <button
                          key={ws.path}
                          onClick={() => {
                            setIsAdminSwitcherOpen(false);
                            onNavigate(ws.path);
                          }}
                          className={`w-full px-3 py-2 rounded-xl flex items-center justify-between text-left text-xs font-medium transition-all cursor-pointer ${
                            isActive
                              ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30'
                              : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                          }`}
                        >
                          <div className="flex items-center gap-2.5">
                            <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                            <span>{ws.name}</span>
                          </div>
                          <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                            {ws.badge}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

        </div>
      </div>

      {/* 3. Right: Export SOP Action + Top-Right Profile Avatar Circle & Dropdown */}
      <div className="flex items-center gap-3" ref={profileRef}>
        
        {/* Export SOP Button */}
        <div className="hidden sm:block">
          <DownloadSOPButton stats={isolationStats} onClick={() => onNavigate('/sop')} />
        </div>

        {/* Top-Right Profile Circle Button */}
        <button
          onClick={() => setIsProfileDropdownOpen(!isProfileDropdownOpen)}
          aria-label="User menu"
          className="relative focus:outline-none cursor-pointer group"
        >
          {currentUser ? (
            /* Logged-In State Avatar */
            <div className={`w-10 h-10 rounded-full text-white font-black text-sm flex items-center justify-center border-2 border-white shadow-md group-hover:scale-105 transition-all ${
              currentUser.portalType === 'admin'
                ? 'bg-slate-900 border-emerald-400'
                : 'bg-[#10b981] shadow-emerald-500/20'
            }`}>
              {currentUser.initials || 'US'}
            </div>
          ) : (
            /* Logged-Out State Avatar */
            <div className="w-10 h-10 rounded-full bg-white/70 backdrop-blur-md border border-white/90 text-slate-600 flex items-center justify-center shadow-sm group-hover:bg-white transition-all">
              <User className="w-5 h-5 text-slate-600" />
            </div>
          )}

          {/* Status Indicator Indicator Dot */}
          <span className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white ${currentUser ? 'bg-emerald-500' : 'bg-slate-400'}`} />
        </button>

        {/* FROSTED GLASS DROPDOWN MENU */}
        {isProfileDropdownOpen && (
          <div className="absolute top-14 right-0 w-80 bg-white/95 backdrop-blur-md border border-slate-200 shadow-2xl rounded-2xl p-2.5 text-slate-900 font-sans animate-in fade-in slide-in-from-top-2 duration-150">
            
            {currentUser ? (
              /* LOGGED-IN DROPDOWN MENU */
              <div className="space-y-2">
                {/* User Header Profile Card */}
                <div className="p-3 rounded-xl bg-slate-100/90 border border-slate-200/80">
                  <div className="flex items-center gap-2.5">
                    <div className={`w-9 h-9 rounded-full text-white font-bold text-xs flex items-center justify-center shrink-0 ${
                      currentUser.portalType === 'admin' ? 'bg-slate-900 border border-emerald-400' : 'bg-[#10b981]'
                    }`}>
                      {currentUser.initials}
                    </div>
                    <div className="overflow-hidden">
                      <h4 className="text-xs font-black text-slate-900 truncate">
                        {currentUser.name}
                      </h4>
                      <p className="text-[10px] text-slate-500 font-mono truncate">
                        {currentUser.phone || currentUser.email}
                      </p>
                    </div>
                  </div>

                  {/* Persona / Role Badge Pill */}
                  <div className="mt-2.5 flex flex-wrap items-center justify-between gap-1">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                      currentUser.portalType === 'admin'
                        ? 'bg-slate-900 text-emerald-400 border border-slate-700'
                        : currentUser.persona === 'resident'
                        ? 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                        : 'bg-amber-100 text-amber-900 border border-amber-300'
                    }`}>
                      {currentUser.portalType === 'admin' ? (
                        <Shield className="w-3 h-3 text-emerald-400" />
                      ) : currentUser.persona === 'resident' ? (
                        <User className="w-3 h-3" />
                      ) : (
                        <Compass className="w-3 h-3" />
                      )}
                      <span className="truncate max-w-[170px]">
                        {currentUser.portalType === 'admin'
                          ? (currentUser.subRole || 'Head Admin')
                          : currentUser.persona === 'resident'
                          ? 'Local Resident'
                          : 'Tourist / Visitor'}
                      </span>
                    </span>

                    <span className="text-[10px] font-semibold text-slate-500 truncate">
                      {currentUser.districtOrCorridor}
                    </span>
                  </div>
                </div>

                {/* Logged-In Actions for Regular Users */}
                <div className="space-y-0.5 text-xs font-semibold text-slate-700">
                  <button
                    onClick={() => {
                      setIsProfileDropdownOpen(false);
                      onNavigate('/report');
                    }}
                    className="w-full px-3 py-2 rounded-lg hover:bg-slate-100 flex items-center gap-2 text-left transition-colors cursor-pointer"
                  >
                    <FileCheck className="w-4 h-4 text-emerald-600" />
                    <span>My Submitted Reports</span>
                  </button>

                  <button
                    onClick={() => {
                      setIsProfileDropdownOpen(false);
                      onNavigate('/');
                    }}
                    className="w-full px-3 py-2 rounded-lg hover:bg-slate-100 flex items-center gap-2 text-left transition-colors cursor-pointer"
                  >
                    <Bookmark className="w-4 h-4 text-emerald-600" />
                    <span>Saved Routes &amp; Alerts</span>
                  </button>

                  <button
                    onClick={() => {
                      setIsProfileDropdownOpen(false);
                      onNavigate('/report');
                    }}
                    className="w-full px-3 py-2 rounded-lg hover:bg-slate-100 flex items-center gap-2 text-left transition-colors cursor-pointer"
                  >
                    <Smartphone className="w-4 h-4 text-emerald-600" />
                    <span>Report Hazard</span>
                  </button>

                  {/* Head Admin Quick Link */}
                  {isHeadAdmin && (
                    <button
                      onClick={() => {
                        setIsProfileDropdownOpen(false);
                        onNavigate('/admin/system');
                      }}
                      className="w-full px-3 py-2 rounded-lg bg-slate-900 text-emerald-400 hover:bg-slate-800 flex items-center gap-2 text-left font-bold transition-colors cursor-pointer mt-1"
                    >
                      <Shield className="w-4 h-4 text-emerald-400" />
                      <span>System &amp; Platform Control</span>
                    </button>
                  )}
                </div>

                <div className="border-t border-slate-200/80 my-1" />

                {/* Log Out Button */}
                <button
                  onClick={() => {
                    setIsProfileDropdownOpen(false);
                    onLogout();
                  }}
                  className="w-full px-3 py-2 rounded-lg hover:bg-rose-50 text-rose-600 flex items-center gap-2 text-xs font-bold text-left transition-colors cursor-pointer"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Log Out</span>
                </button>
              </div>
            ) : (
              /* LOGGED-OUT DROPDOWN MENU */
              <div className="space-y-1 text-xs font-semibold text-slate-800">
                <div className="px-3 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Authentication Access
                </div>

                {/* Sign In */}
                <button
                  onClick={() => {
                    setIsProfileDropdownOpen(false);
                    onOpenAuth(false); // isRegisterMode = false
                  }}
                  className="w-full px-3 py-2 rounded-lg hover:bg-emerald-50 text-emerald-900 flex items-center justify-between text-left transition-colors cursor-pointer font-bold"
                >
                  <div className="flex items-center gap-2">
                    <LogIn className="w-4 h-4 text-[#10b981]" />
                    <span>Sign In</span>
                  </div>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400 -rotate-90" />
                </button>

                {/* Create Safety Account */}
                <button
                  onClick={() => {
                    setIsProfileDropdownOpen(false);
                    onOpenAuth(true); // isRegisterMode = true
                  }}
                  className="w-full px-3 py-2 rounded-lg hover:bg-emerald-50 text-emerald-900 flex items-center justify-between text-left transition-colors cursor-pointer font-bold"
                >
                  <div className="flex items-center gap-2">
                    <UserPlus className="w-4 h-4 text-[#10b981]" />
                    <span>Create Safety Account</span>
                  </div>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400 -rotate-90" />
                </button>

                <div className="border-t border-slate-200/80 my-1" />

                {/* Report Hazard as Guest */}
                <button
                  onClick={() => {
                    setIsProfileDropdownOpen(false);
                    onNavigate('/report');
                  }}
                  className="w-full px-3 py-2 rounded-lg hover:bg-slate-100 text-slate-700 flex items-center gap-2 text-left transition-colors cursor-pointer"
                >
                  <ShieldAlert className="w-4 h-4 text-amber-600" />
                  <span>Report Hazard as Guest</span>
                </button>
              </div>
            )}

          </div>
        )}

      </div>

    </header>
  );
};
