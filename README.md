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
docker compose stop redis
curl http://localhost:8000/risk-state   # should still return real data, just slower
docker compose start redis
```

## Project layout

```
app/
  main.py                # creates the app, includes every router & /demo UI
  database.py            # Postgres connection with fallback
  redis_client.py        # Redis connection with fallback
  comms/                 # Member 6 Communications & Bot Engine
    vernacular.py        # 6 North East languages + accessibility icons + IVR
    classifier.py        # AI CV hazard classifier (MobileNetV3 + Edge)
    sample_media.py      # Curated sample hazard media generator
    cap_engine.py        # ITU-T X.1303 / NDMA SACHET CAP v1.2 engine
    queue_service.py     # DEOC human-in-the-loop verification queue
    bot_engine.py        # Stateful two-way WhatsApp conversation engine
    twilio_client.py     # WhatsApp client (live Twilio + local simulator)
    dispatcher.py        # Cross-team alert trigger & geofenced dispatcher
    event_stream.py      # SSE real-time feed for Member 5's 3D GIS
  routers/
    telemetry.py         # Member 4 (IoT hardware)
    risk.py              # Member 2 + Member 3 + Member 5 (Dual engine)
    reports.py           # Member 6 crowdsourced field reports
    villages.py          # Member 3 isolation output
    comms.py             # Member 6 WhatsApp webhooks, CAP, queue, & simulator
  static/demo/index.html # Interactive Day 4 Judge Demo Console & WhatsApp Phone
init.sql                 # schema with updated reports table
```

---

## Member 6: Communications & Bot Developer System

Member 6 owns the **human-interaction loop**, delivering a zero-barrier experience for citizens, Aapda Mitra volunteers, and District Emergency Operation Center (DEOC) operators.

### 🌟 Core Capabilities Built:
1. **Two-Way Zero-App Interface (WhatsApp / Twilio / Meta)**:
   - Citizens and volunteers need no custom app; they report directly via WhatsApp.
   - Handles text, photo attachments, and WhatsApp GPS location pins.
   - Stateful conversational session engine with multi-step reporting, safe shelter lookups, and emergency SOS hotlines.
2. **Multilingual & Vernacular Adaptation**:
   - Dynamic alert translation across the **6 primary North East regional languages**:
     - Assamese (অসমীয়া)
     - Khasi (Ka Ktien Khasi)
     - Mizo (Mizo ṭawng)
     - Manipuri / Meiteilon (ꯃꯩꯇꯩꯂꯣꯟ)
     - Bengali (বাংলা)
     - English
   - Non-literate visual icons & emoji cues (`⚠️`, `🚨`, `⛰️`, `🪨`, `🛣️`, `🏃`, `⛺`, `📞`, `📍`, `📸`).
   - Audio / IVR voice prompt scripts for audio notes and voice helplines.
3. **AI-Assisted Field Media Verification Pipeline**:
   - Lightweight computer-vision classifier (`MobileNetV3` + texture/edge spectral analysis).
   - Ingests field photos and automatically outputs preliminary classification tags and calibrated confidence scores (e.g. `Tag: Surface Rockfall | Confidence: 90.1% | Latency: 11.6ms`).
   - Categorizes into: `Road Tension Crack`, `Surface Rockfall`, `Landslide Scar / Mudflow`, `Blocked Culvert / Drainage Failure`, `Normal / No Hazard`.
4. **Human-in-the-Loop Governance & Member 5 Queue**:
   - Crowdsourced field reports enter a dedicated `PENDING_REVIEW` queue.
   - Submissions serve as supporting evidence for human officers and **never directly alter regional threat levels**.
   - DEOC officers approve or reject reports; approved reports push into Member 5's live 3D GIS incident layer via SSE real-time stream (`/api/comms/stream`).
5. **National Alerting Protocol (CAP) Compliance**:
   - Complies with **ITU-T X.1303** and **NDMA SACHET** Common Alerting Protocol v1.2.
   - Generates official XML and JSON feeds (`/api/comms/cap/{id}.xml` and `/api/comms/cap/{id}.json`).
   - Automatically embeds Member 3's Isolation Twin metrics (cut-off villages, affected population, designated bypass routes).

---

## ⚡ Day 4 Live Demo Console & WhatsApp Simulator

Open the interactive Web Demo Console directly in your browser:
```
http://localhost:8000/demo
```
The console provides:
- A **Virtual WhatsApp Smartphone** running the live bot (interactive numbered chips, photo attachments, location pins, multilingual switching).
- A **Live Computer Vision Inspector** visualizing real-time MobileNet inference, confidence meters, and visual feature descriptors.
- A **DEOC Review Queue** for Member 5's dashboard (1-click Approve / Reject).
- An **NDMA SACHET CAP Feed** showing standard XML generation and one-click alert dispatch.
- A **"Run Day 4 Live Demo" button** that executes the full round-trip flow for the judges automatically!

### Connecting Real WhatsApp Tokens (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
And add your credentials:
```ini
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```
*(If no tokens are set, the system automatically runs in zero-friction Simulation Mode so testing and demonstrations always work smoothly!)*

### Running Automated Tests
```bash
python tests/run_all_tests.py
```

