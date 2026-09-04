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
