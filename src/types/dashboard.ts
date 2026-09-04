export interface UserProfile {
  name: string;
  phone?: string;
  email?: string;
  portalType: 'user' | 'admin';
  persona: 'resident' | 'tourist' | 'head_admin' | 'role_admin';
  subRole?: string; // e.g. Geotechnical & Meteorological Officer, Incident Moderation Admin, etc.
  districtOrCorridor: string;
  initials: string;
  avatarUrl?: string;
}

export interface RiskPolygon {
  id: string;
  name: string;
  severity: 'LEVEL 1' | 'LEVEL 2' | 'LEVEL 3';
  instabilityScore: number; // 0 to 100%
  primaryTrigger: 'Soil Saturation' | 'Tilt Acceleration' | 'Seismic Activity';
  coords: [number, number][]; // Polygon vertices
  lastUpdated?: string;
  authorInfo?: string;
}

export interface GeotechSensor {
  id: string;
  name: string;
  type: 'Piezometer' | 'Tiltmeter' | 'Pore Pressure Sensor' | 'Seismometer';
  lat: number;
  lng: number;
  tiltRateLimit: number; // default 2.5 mm/hr
  moistureLimit: number; // default 60%
  status: 'active' | 'warning' | 'calibrating';
}

export interface IoTNode {
  id: string;
  name: string;
  lat: number;
  lng: number;
  tiltChange: number; // in degrees or mm displacement
  moisture: number; // in percentage
  battery?: number; // percentage
  status?: 'normal' | 'warning' | 'critical';
  lastUpdated?: string;
}

export interface CitizenIncident {
  id: string;
  lat: number;
  lng: number;
  photoUrl: string;
  tag: 'Rockfall' | 'Road Crack' | 'Mudslide' | 'Flooding' | 'Tree Collapse' | string;
  confidence: number; // e.g. 0.942 -> 94.2%
  timestamp: string;
  status?: 'pending' | 'approved' | 'rejected';
  verificationStatus?: 'unverified' | 'verified_onsite' | 'false_alarm' | 'approved';
  submissionPersona?: 'Local Resident' | 'Tourist / Traveler';
  accuracyRadiusMeters?: number;
  isClusterFlagged?: boolean;
  operatorLog?: string;
  mergedIntoId?: string;
  multiPhotos?: string[];
  locationName?: string;
  reporterPhone?: string;
  description?: string;
}

export interface IsolationStats {
  isolatedPopulation: number;
  cutoffVillagesCount: number;
  primaryCutoffRoad: string;
  estimatedClearingTimeHours: number;
  strandedPhcCount?: number;
  detourKm?: number;
  delayMins?: number;
  cutoffVillagesList?: string[];
}

export interface RoadDisconnect {
  id: string;
  name: string;
  route: string;
  detourKm: number;
  delayMins: number;
  status: 'BLOCKED' | 'IMPASSABLE' | 'RESTRICTED';
  lat: number;
  lng: number;
  affectedVillages: string[];
}

export interface TelemetryData {
  displacementMm: number;
  displacementTrend: 'stable' | 'rising' | 'critical';
  moisturePercent: number;
  rainfallMmHr: number;
  seismicG: number;
  threatLevel: 'LEVEL 1' | 'LEVEL 2' | 'LEVEL 3' | 'LEVEL 4 CRITICAL';
}

export interface DispatchTask {
  id: string;
  agency: 'BRO' | 'NDRF' | 'SDRF' | 'District Police' | 'IAF Cell';
  taskName: string;
  commanderName: string;
  priority: 'Urgent' | 'Standard';
  targetSector: string;
  timestamp: string;
  status: 'En Route' | 'On-Site Ops Active' | 'Cleared';
}

export interface BroadcastAlert {
  id: string;
  channels: ('SMS' | 'WhatsApp' | 'Siren')[];
  audience: 'All Corridor Users' | 'Local Residents (Geofenced)' | 'Tourists / Travelers';
  message: string;
  recipientsCount: number;
  authorizedAt: string;
  threatLevel: 'LEVEL 1' | 'LEVEL 2' | 'LEVEL 3';
}

export interface RouteStatus {
  id: string;
  name: string;
  corridor: string;
  state: 'CLEAR' | 'DETOUR' | 'SEVERED';
  clearanceNotes: string;
  lastUpdated: string;
}

export interface FieldResourceState {
  personnel: {
    ndrf: number;
    sdrf: number;
    bro: number;
    police: number;
  };
  machinery: {
    excavators: number;
    earthmovers: number;
    bulldozers: number;
    ambulances: number;
  };
  machineryStatus: 'Operational' | 'Requires Fuel/Maintenance';
  medicalSupplies: 'Sufficient' | 'Low' | 'Critical';
  rations: 'Sufficient' | 'Low';
  satellitePhone: 'Active' | 'Weak';
}

export interface UserAccount {
  id: string;
  name: string;
  contact: string;
  category: 'User' | 'Admin';
  role: string;
  status: 'Active' | 'Suspended' | 'Pending';
  lastLogin: string;
}

export interface SystemLog {
  id: string;
  timestamp: string;
  actor: string;
  actorRole: string;
  action: string;
  zone: 'Zone 1' | 'Zone 2' | 'Zone 3' | 'Zone 4' | 'Global';
  ipAddress: string;
  severity: 'Info' | 'Warning' | 'Critical Security Event';
}
