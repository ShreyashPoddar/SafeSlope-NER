import React, { useState } from 'react';
import {
  ShieldCheck,
  User,
  Phone,
  Mail,
  Lock,
  ArrowRight,
  Landmark,
  Smartphone,
  Clock,
  KeyRound,
  ArrowLeft,
  Shield,
  Layers,
  ChevronDown,
  Activity,
  UserCheck
} from 'lucide-react';
import type { UserProfile } from '../types/dashboard';
import { useAuth } from '../hooks/useAuth.tsx';
import { ApiError } from '../api/client';

interface AuthPageProps {
  onLoginSuccess: (user: UserProfile) => void;
  onEmergencyReport: () => void;
  onBackToDashboard?: () => void;
  initialRegisterMode?: boolean;
}

type PortalType = 'user' | 'admin';
type UserRoleType = 'resident' | 'tourist';
type AdminRoleType = 'head_admin' | 'role_admin';
type AdminSubRoleType = 
  | 'geotechnical' 
  | 'incident_moderation' 
  | 'emergency_dispatch' 
  | 'field_operations';

type AuthMethod = 'otp' | 'password';

export const AuthPage: React.FC<AuthPageProps> = ({
  onLoginSuccess,
  onEmergencyReport,
  onBackToDashboard,
  initialRegisterMode = true
}) => {
  // Mode State
  const [isRegisterMode, setIsRegisterMode] = useState<boolean>(initialRegisterMode);
  const [authMethod, setAuthMethod] = useState<AuthMethod>('otp');

  // Tier 1: Primary Account Type
  const [portalType, setPortalType] = useState<PortalType>('user');

  // Tier 2: Secondary Role
  const [userRole, setUserRole] = useState<UserRoleType>('resident');
  const [adminRole, setAdminRole] = useState<AdminRoleType>('role_admin');

  // Tier 3: Tertiary Sub-Role (For Role-Based Admin)
  const [adminSubRole, setAdminSubRole] = useState<AdminSubRoleType>('emergency_dispatch');

  // Form Fields
  const [phoneNumber, setPhoneNumber] = useState<string>('');
  const [emergencyPhone, setEmergencyPhone] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [adminPasscode, setAdminPasscode] = useState<string>('');
  const [district, setDistrict] = useState<string>('Aizawl (Hunthar Sector)');
  const [homeSector, setHomeSector] = useState<string>('Hunthar Veng Slope');
  const [travelCorridor, setTravelCorridor] = useState<string>('NH-6 Sonapur Transit');
  const [durationOfStay, setDurationOfStay] = useState<string>('4 - 7 Days (Tourist Trip)');

  // OTP Verification State
  const [otpSent, setOtpSent] = useState<boolean>(false);
  const [otpCode, setOtpCode] = useState<string>('');
  const [resendTimer, setResendTimer] = useState<number>(30);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const { loginWithDemo } = useAuth();

  // Helper for Sub-Role Label
  const getSubRoleTitle = (roleKey: AdminSubRoleType): string => {
    switch (roleKey) {
      case 'geotechnical':
        return 'Geotechnical & Meteorological Officer';
      case 'incident_moderation':
        return 'Incident Moderation & Citizen Report Admin';
      case 'emergency_dispatch':
        return 'Emergency Dispatch & DDMA Nodal Officer';
      case 'field_operations':
        return 'First Responder / Field Operations Officer';
      default:
        return 'SDMA Operations Officer';
    }
  };

  // Handle Send OTP
  const handleSendOtp = (e: React.FormEvent) => {
    e.preventDefault();
    if (!phoneNumber) return;
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      setOtpSent(true);
      setResendTimer(30);
    }, 800);
  };

  // Build fallback UserProfile (used when backend is offline)
  const buildFallbackProfile = (): UserProfile => {
    if (portalType === 'user') {
      if (userRole === 'resident') {
        return { name: 'Lalrinpuia Sailo', phone: phoneNumber || '+91 98625 11234', email: email || 'lalrinpuia@gmail.com', portalType: 'user', persona: 'resident', districtOrCorridor: `${district} • ${homeSector}`, initials: 'LS' };
      } else {
        return { name: 'Alex Traveler', phone: phoneNumber || '+91 98625 99881', email: email || 'alex.traveler@gmail.com', portalType: 'user', persona: 'tourist', districtOrCorridor: `${travelCorridor} (${durationOfStay})`, initials: 'AT' };
      }
    } else {
      if (adminRole === 'head_admin') {
        return { name: 'Smt. Zoramthangi Lunglei, IAS', email: email || 'commissioner@gmail.com', portalType: 'admin', persona: 'head_admin', subRole: 'State Disaster Relief Commissioner & Chairperson', districtOrCorridor: 'NER Command Center', initials: 'ZL' };
      } else {
        const subTitle = getSubRoleTitle(adminSubRole);
        return { name: 'Dr. Lalrinpuia Sailo, IAS', email: email || 'nodal.officer@gmail.com', portalType: 'admin', persona: 'role_admin', subRole: subTitle, districtOrCorridor: 'Hunthar-Sonapur Sector', initials: 'LS' };
      }
    }
  };

  // Handle Complete Login / Register — calls backend, falls back to local profile on error
  const handleVerifyAndSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setApiError(null);
    try {
      const persona = portalType === 'user' ? (userRole as UserProfile['persona']) : (adminRole as UserProfile['persona']);
      const subRole = portalType === 'admin' && adminRole === 'role_admin' ? getSubRoleTitle(adminSubRole) : undefined;
      const district_val = portalType === 'user'
        ? (userRole === 'resident' ? `${district} • ${homeSector}` : `${travelCorridor} (${durationOfStay})`)
        : (adminRole === 'head_admin' ? 'NER Command Center' : 'Hunthar-Sonapur Sector');
      const profile = await loginWithDemo({
        portal_type: portalType,
        persona,
        sub_role: subRole,
        email: email || undefined,
        district: district_val,
      });
      onLoginSuccess(profile);
    } catch (err) {
      if (err instanceof ApiError && err.status >= 500) {
        // Backend unavailable — fall back to local profile
        const profile = buildFallbackProfile();
        onLoginSuccess(profile);
      } else {
        setApiError(err instanceof Error ? err.message : 'Login failed. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Fast-track Social Auth
  const handleSocialAuth = async () => {
    setApiError(null);
    try {
      const profile = await loginWithDemo({ portal_type: 'user', persona: 'resident' });
      onLoginSuccess(profile);
    } catch {
      // Offline fallback
      onLoginSuccess({ name: 'Lalrinpuia Sailo', phone: '+91 98625 11234', email: 'name@gmail.com', portalType: 'user', persona: 'resident', districtOrCorridor: 'Aizawl (Hunthar Sector)', initials: 'LS' });
    }
  };

  return (
    <div className="min-h-screen text-slate-900 font-sans selection:bg-[#10b981] selection:text-white flex flex-col justify-between items-center p-4 md:p-6">
      
      {/* Viewport Top Header Bar */}
      <header className="max-w-6xl w-full mx-auto flex items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-3">
          {onBackToDashboard && (
            <button
              onClick={onBackToDashboard}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-white/70 hover:bg-white/90 text-slate-800 text-xs font-bold transition-all border border-white/90 shadow-sm cursor-pointer active:scale-95 backdrop-blur-md"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Dashboard</span>
            </button>
          )}
          
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-[#10b981] text-white flex items-center justify-center font-black text-sm shadow-md shadow-emerald-500/20">
              S
            </div>
            <div>
              <span className="font-extrabold text-slate-900 tracking-tight text-sm">SafeSlope-NER</span>
              <span className="text-[10px] text-emerald-800 font-mono block -mt-1 font-semibold">
                SDMA Early Warning Network
              </span>
            </div>
          </div>
        </div>

        {/* Government Alignment Badge */}
        <div className="hidden sm:flex items-center gap-2 bg-emerald-500/20 backdrop-blur-md px-3 py-1 rounded-full border border-emerald-500/40 text-[11px] font-bold text-emerald-900">
          <Landmark className="w-3.5 h-3.5 text-emerald-800" />
          <span>Official Regional Safety Portal — SDMA North East</span>
        </div>
      </header>

      {/* CENTERED SINGLE AUTHENTICATION CARD */}
      <main className="max-w-lg w-full mx-auto my-auto glass-panel-light p-6 md:p-8 rounded-3xl border border-white/90 shadow-2xl backdrop-blur-3xl flex flex-col justify-between gap-6">
        
        {/* Card Top: Mode Switcher & Title */}
        <div className="space-y-4">
          
          <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-emerald-100 text-[#10b981] flex items-center justify-center font-bold">
                <UserCheck className="w-4 h-4 text-[#10b981]" />
              </div>
              <div>
                <h2 className="text-lg font-black text-slate-900 tracking-tight">
                  {isRegisterMode ? 'Create Safety Account' : 'Sign In to Portal'}
                </h2>
                <p className="text-[11px] text-slate-500 font-medium">
                  {portalType === 'user' ? 'Disaster alerts & rapid hazard reporting' : 'SDMA Command & Control Administration'}
                </p>
              </div>
            </div>

            <button
              onClick={() => {
                setIsRegisterMode(!isRegisterMode);
                setOtpSent(false);
              }}
              className="text-xs font-bold text-[#10b981] hover:text-[#059669] underline cursor-pointer"
            >
              {isRegisterMode ? 'Sign In' : 'Register'}
            </button>
          </div>

          {/* MULTI-TIER ROLE DROPDOWN SELECTION */}
          <div className="space-y-3 p-3.5 rounded-2xl glass-panel-inner border border-white/80 shadow-inner">
            
            {/* TIER 1: Primary Account Type Dropdown (User vs Admin) */}
            <div>
              <label className="block text-[11px] font-extrabold uppercase tracking-wider text-slate-600 mb-1">
                1. Select Portal Type
              </label>
              <div className="relative">
                <Shield className="w-4 h-4 text-emerald-600 absolute left-3 top-2.5" />
                <select
                  value={portalType}
                  onChange={(e) => setPortalType(e.target.value as PortalType)}
                  className="w-full pl-9 pr-8 py-2 rounded-xl bg-white/90 border border-slate-300 focus:border-[#10b981] text-xs font-bold text-slate-900 outline-none cursor-pointer appearance-none shadow-sm"
                >
                  <option value="user">User (Citizen &amp; Traveler Portal)</option>
                  <option value="admin">Admin (SDMA Command &amp; Control)</option>
                </select>
                <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 top-2.5 pointer-events-none" />
              </div>
            </div>

            {/* TIER 2: Secondary Role Dropdown (Dependent on Tier 1) */}
            <div>
              <label className="block text-[11px] font-extrabold uppercase tracking-wider text-slate-600 mb-1">
                2. Select Account Role
              </label>
              <div className="relative">
                {portalType === 'user' ? (
                  <User className="w-4 h-4 text-emerald-600 absolute left-3 top-2.5" />
                ) : (
                  <Layers className="w-4 h-4 text-emerald-600 absolute left-3 top-2.5" />
                )}
                
                {portalType === 'user' ? (
                  <select
                    value={userRole}
                    onChange={(e) => setUserRole(e.target.value as UserRoleType)}
                    className="w-full pl-9 pr-8 py-2 rounded-xl bg-white/90 border border-slate-300 focus:border-[#10b981] text-xs font-bold text-slate-900 outline-none cursor-pointer appearance-none shadow-sm"
                  >
                    <option value="resident">Local Resident (SMS Disaster Warnings &amp; Panchayat)</option>
                    <option value="tourist">Tourist / Traveler (Transit Corridor &amp; Emergency SOS)</option>
                  </select>
                ) : (
                  <select
                    value={adminRole}
                    onChange={(e) => setAdminRole(e.target.value as AdminRoleType)}
                    className="w-full pl-9 pr-8 py-2 rounded-xl bg-white/90 border border-slate-300 focus:border-[#10b981] text-xs font-bold text-slate-900 outline-none cursor-pointer appearance-none shadow-sm"
                  >
                    <option value="role_admin">Role-Based Admin (Specialized Division Officer)</option>
                    <option value="head_admin">Head Admin (Full Platform Access)</option>
                  </select>
                )}
                <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 top-2.5 pointer-events-none" />
              </div>
            </div>

            {/* TIER 3: Tertiary Sub-Role Dropdown (Triggered ONLY when Role-Based Admin is active) */}
            {portalType === 'admin' && adminRole === 'role_admin' && (
              <div className="pt-1 border-t border-slate-200/80 animate-in fade-in duration-200">
                <label className="block text-[11px] font-extrabold uppercase tracking-wider text-emerald-800 mb-1">
                  3. Select Officer Division Sub-Role
                </label>
                <div className="relative">
                  <Activity className="w-4 h-4 text-emerald-600 absolute left-3 top-2.5" />
                  <select
                    value={adminSubRole}
                    onChange={(e) => setAdminSubRole(e.target.value as AdminSubRoleType)}
                    className="w-full pl-9 pr-8 py-2 rounded-xl bg-white/90 border border-emerald-400 text-xs font-extrabold text-emerald-950 outline-none cursor-pointer appearance-none shadow-sm"
                  >
                    <option value="geotechnical">Geotechnical &amp; Meteorological Officer (Sensors &amp; Polygons)</option>
                    <option value="incident_moderation">Incident Moderation &amp; Citizen Report Admin (Zone 4 Queue)</option>
                    <option value="emergency_dispatch">Emergency Dispatch &amp; DDMA Nodal Officer (SOP Gazette Orders)</option>
                    <option value="field_operations">First Responder / Field Operations Officer (BRO &amp; Clearance Logs)</option>
                  </select>
                  <ChevronDown className="w-4 h-4 text-emerald-600 absolute right-3 top-2.5 pointer-events-none" />
                </div>
              </div>
            )}

          </div>

        </div>

        {/* Dynamic Authentication Form Credentials Body */}
        {portalType === 'user' ? (
          /* USER AUTHENTICATION METHOD (Mobile OTP vs Email) */
          <div>
            <div className="flex items-center gap-4 border-b border-slate-200/80 pb-2 text-xs font-bold mb-3">
              <button
                type="button"
                onClick={() => {
                  setAuthMethod('otp');
                  setOtpSent(false);
                }}
                className={`pb-1 flex items-center gap-1.5 transition-colors cursor-pointer border-b-2 ${
                  authMethod === 'otp'
                    ? 'border-[#10b981] text-emerald-800 font-extrabold'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                <Smartphone className="w-3.5 h-3.5" />
                <span>1-Tap Mobile OTP</span>
              </button>

              <button
                type="button"
                onClick={() => setAuthMethod('password')}
                className={`pb-1 flex items-center gap-1.5 transition-colors cursor-pointer border-b-2 ${
                  authMethod === 'password'
                    ? 'border-[#10b981] text-emerald-800 font-extrabold'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                <Mail className="w-3.5 h-3.5" />
                <span>Email &amp; Password</span>
              </button>
            </div>

            {authMethod === 'otp' ? (
              <form onSubmit={otpSent ? handleVerifyAndSubmit : handleSendOtp} className="space-y-3.5">
                {!otpSent ? (
                  <>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Mobile Number (for SMS Alerts)
                      </label>
                      <div className="relative">
                        <Phone className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                        <input
                          type="tel"
                          required
                          placeholder="+91 98765 43210"
                          value={phoneNumber}
                          onChange={(e) => setPhoneNumber(e.target.value)}
                          className="w-full pl-10 pr-4 py-2 rounded-xl bg-white/80 border border-slate-300 focus:border-[#10b981] text-xs font-semibold outline-none"
                        />
                      </div>
                    </div>

                    {isRegisterMode && (
                      userRole === 'resident' ? (
                        <div className="grid grid-cols-2 gap-2.5">
                          <div>
                            <label className="block text-[11px] font-bold text-slate-700 mb-1">District</label>
                            <select
                              value={district}
                              onChange={(e) => setDistrict(e.target.value)}
                              className="w-full px-2.5 py-2 rounded-xl bg-white/80 border border-slate-300 text-xs font-semibold outline-none"
                            >
                              <option value="Aizawl (Hunthar Sector)">Aizawl (Hunthar)</option>
                              <option value="Kolasib District">Kolasib</option>
                              <option value="Lunglei District">Lunglei</option>
                              <option value="East Khasi Hills (Sonapur)">East Khasi Hills</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-[11px] font-bold text-slate-700 mb-1">Home Corridor</label>
                            <select
                              value={homeSector}
                              onChange={(e) => setHomeSector(e.target.value)}
                              className="w-full px-2.5 py-2 rounded-xl bg-white/80 border border-slate-300 text-xs font-semibold outline-none"
                            >
                              <option value="Hunthar Veng Slope">Hunthar Slope</option>
                              <option value="Sonapur Ridge Corridor">Sonapur Ridge</option>
                              <option value="Kolasib Bypass">Kolasib Bypass</option>
                            </select>
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-2.5">
                          <div className="grid grid-cols-2 gap-2.5">
                            <div>
                              <label className="block text-[11px] font-bold text-slate-700 mb-1">Emergency Contact</label>
                              <input
                                type="tel"
                                required
                                placeholder="+91 Contact"
                                value={emergencyPhone}
                                onChange={(e) => setEmergencyPhone(e.target.value)}
                                className="w-full px-2.5 py-2 rounded-xl bg-white/80 border border-slate-300 text-xs font-semibold outline-none"
                              />
                            </div>
                            <div>
                              <label className="block text-[11px] font-bold text-slate-700 mb-1">Stay Duration</label>
                              <select
                                value={durationOfStay}
                                onChange={(e) => setDurationOfStay(e.target.value)}
                                className="w-full px-2.5 py-2 rounded-xl bg-white/80 border border-slate-300 text-xs font-semibold outline-none"
                              >
                                <option value="1 - 3 Days">1 - 3 Days</option>
                                <option value="4 - 7 Days (Tourist Trip)">4 - 7 Days</option>
                                <option value="1 - 2 Weeks">1 - 2 Weeks</option>
                              </select>
                            </div>
                          </div>

                          <div>
                            <label className="block text-[11px] font-bold text-slate-700 mb-1">Transit Corridor</label>
                            <select
                              value={travelCorridor}
                              onChange={(e) => setTravelCorridor(e.target.value)}
                              className="w-full px-2.5 py-2 rounded-xl bg-white/80 border border-slate-300 text-xs font-semibold outline-none"
                            >
                              <option value="NH-6 Sonapur Transit">NH-6 Sonapur Transit</option>
                              <option value="Sikkim-Gangtok Highway">Sikkim-Gangtok</option>
                              <option value="NH-54 Aizawl-Lunglei">NH-54 Aizawl-Lunglei</option>
                            </select>
                          </div>
                        </div>
                      )
                    )}

                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full py-2.5 rounded-xl bg-[#10b981] hover:bg-[#059669] text-white font-extrabold text-xs shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95"
                    >
                      <span>{isSubmitting ? 'Sending Verification OTP...' : 'Send 1-Tap OTP Code'}</span>
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </>
                ) : (
                  <div className="space-y-3">
                    <div className="p-2.5 rounded-xl bg-emerald-100/80 border border-emerald-300 text-xs text-emerald-900 flex items-center justify-between">
                      <span>OTP sent to <strong>{phoneNumber}</strong></span>
                      <button
                        type="button"
                        onClick={() => setOtpSent(false)}
                        className="text-[11px] font-bold text-emerald-700 underline cursor-pointer"
                      >
                        Edit
                      </button>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">Enter 4-Digit Security Code</label>
                      <div className="relative">
                        <KeyRound className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                        <input
                          type="text"
                          maxLength={6}
                          required
                          placeholder="••••"
                          value={otpCode}
                          onChange={(e) => setOtpCode(e.target.value)}
                          className="w-full pl-10 pr-4 py-2 rounded-xl bg-white/80 border border-slate-300 text-sm font-mono font-bold tracking-widest outline-none"
                        />
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs text-slate-500 font-mono">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-slate-400" />
                        <span>Resend in {resendTimer}s</span>
                      </span>
                      <button
                        type="button"
                        onClick={() => setResendTimer(30)}
                        className="font-bold text-emerald-700 hover:underline cursor-pointer"
                      >
                        Resend Code
                      </button>
                    </div>

                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full py-2.5 rounded-xl bg-[#10b981] hover:bg-[#059669] text-white font-extrabold text-xs shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95"
                    >
                      <ShieldCheck className="w-4 h-4" />
                      <span>{isSubmitting ? 'Verifying...' : 'Verify & Continue'}</span>
                    </button>
                  </div>
                )}
              </form>
            ) : (
              <form onSubmit={handleVerifyAndSubmit} className="space-y-3.5">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Email Address</label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                    <input
                      type="email"
                      required
                      placeholder="name@gmail.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 rounded-xl bg-white/80 border border-slate-300 text-xs font-semibold outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Password</label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                    <input
                      type="password"
                      required
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 rounded-xl bg-white/80 border border-slate-300 text-xs font-semibold outline-none"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full py-2.5 rounded-xl bg-[#10b981] hover:bg-[#059669] text-white font-extrabold text-xs shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95"
                >
                  <span>{isSubmitting ? 'Authenticating...' : isRegisterMode ? 'Register Account' : 'Sign In'}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </form>
            )}

            {/* Social Single Sign-On Shortcuts */}
            <div className="mt-3 pt-2.5 border-t border-slate-200/80">
              <div className="grid grid-cols-2 gap-2.5">
                <button
                  type="button"
                  onClick={handleSocialAuth}
                  className="py-2 px-3 rounded-xl bg-white/90 text-slate-700 border border-slate-300 text-xs font-bold flex items-center justify-center gap-2 shadow-sm hover:bg-white cursor-pointer"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24">
                    <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.6l3.1-3.1C17.3 1.7 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.4 9 5 12 5z"/>
                    <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.8z"/>
                  </svg>
                  <span>Google</span>
                </button>

                <button
                  type="button"
                  onClick={handleSocialAuth}
                  className="py-2 px-3 rounded-xl bg-emerald-700 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-sm hover:bg-emerald-800 cursor-pointer"
                >
                  <Phone className="w-3.5 h-3.5 fill-white" />
                  <span>WhatsApp</span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* ADMIN AUTHENTICATION CREDENTIALS FORM */
          <form onSubmit={handleVerifyAndSubmit} className="space-y-3.5">
            
            <div className="p-2.5 rounded-xl bg-slate-900 text-white text-xs font-mono flex items-center justify-between border border-emerald-500/40">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-emerald-400 shrink-0" />
                <div>
                  <div className="text-emerald-400 font-bold text-[11px]">
                    {adminRole === 'head_admin' ? 'SUPER ADMIN PRIVILEGES' : 'DIVISIONAL OFFICER LEVEL'}
                  </div>
                  <div className="text-[9px] text-slate-300">
                    {adminRole === 'head_admin' ? 'Full Command & Control Access' : getSubRoleTitle(adminSubRole)}
                  </div>
                </div>
              </div>
              <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[9px] font-bold">
                RESTRICTED
              </span>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Official Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="email"
                  required
                  placeholder="name@gmail.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 rounded-xl bg-white/80 border border-slate-300 text-xs font-semibold outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Admin Security Passcode</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="password"
                  required
                  placeholder="••••••••••••"
                  value={adminPasscode}
                  onChange={(e) => setAdminPasscode(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 rounded-xl bg-white/80 border border-slate-300 text-xs font-semibold outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-950 text-white font-extrabold text-xs shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95 border border-emerald-500/30"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>{isSubmitting ? 'Authenticating Clearance...' : 'Authenticate Admin Access'}</span>
            </button>

            {/* API Error Message */}
            {apiError && (
              <div className="px-3 py-2 rounded-xl bg-rose-100 border border-rose-300 text-rose-700 text-xs font-semibold flex items-start gap-2">
                <span className="mt-0.5">⚠</span>
                <span>{apiError}</span>
              </div>
            )}

          </form>
        )}


        {/* Emergency Direct Pass Link */}
        <div className="pt-2 text-center border-t border-slate-200/80">
          <p className="text-xs text-slate-600 font-medium">
            In an immediate emergency?{' '}
            <button
              onClick={onEmergencyReport}
              className="font-black text-rose-600 hover:text-rose-700 underline cursor-pointer"
            >
              Continue as Guest to report a hazard without logging in.
            </button>
          </p>
        </div>

      </main>

      {/* Footer */}
      <footer className="max-w-6xl w-full mx-auto text-center text-[11px] text-slate-500 font-medium mt-4">
        SafeSlope-NER Disaster Warning System • State Disaster Management Authority (SDMA) • Mizoram / Meghalaya / Assam
      </footer>

    </div>
  );
};
