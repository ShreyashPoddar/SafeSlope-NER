# SafeSlope-NER: Disaster Management & Command Center

SafeSlope-NER is an integrated landslide monitoring, risk assessment, SOP evacuation dispatch, and citizen incident reporting system built for North Eastern India (NER).

---

## 🚀 Frontend: SafeSlope Control Room & Citizen Reporting Subsystem
- **Framework**: React 19 + TypeScript + Vite + Tailwind CSS
- **Features**:
  - **Zone 1 GIS Map Viewport**: Esri Topo Map tiles, North Eastern hill corridor, real-time IoT sensors & active landslide heatmap circles.
  - **Zone 2 Telemetry Analytics**: Multi-axis X, Y, Z displacement sensor charts, Soil Moisture saturation, and 87% ML Hazard Risk score.
  - **Zone 3 Critical Isolation Panel**: Isolated population metrics, cutoff community stats, and focus map triggers for NH-6 Sonapur Cut & NH-54 Aizawl Cut.
  - **Zone 4 Moderation Queue**: Human-in-the-loop WhatsApp citizen photo ingest cards with AI label badges and Approve/Reject triage buttons.
  - **SOP Emergency Dispatch Order (`/sop`)**: Formal A4 printable SDMA North Eastern Region (NER) dispatch document with @react-pdf/renderer PDF download support.
  - **Mobile Citizen Incident Reporting (`/report`)**: Mobile camera photo upload, auto GPS geolocation, hazard type selection, and instant command grid dispatch.

### Quick Start Frontend
```bash
npm install
npm run dev
```

---

## 🛠️ Backend: SafeSlope-NER API Gateway
FastAPI + PostgreSQL/PostGIS + Redis.

### Quick Start Backend
```bash
docker compose up --build
```
Then open http://localhost:8000/docs to view and test API endpoints.
