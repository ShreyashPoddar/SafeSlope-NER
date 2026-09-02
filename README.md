# SafeSlope-NER

A Named Entity Recognition (NER) project focused on geotechnical and slope safety data.

## Overview

SafeSlope-NER aims to extract structured information from unstructured geotechnical reports, slope stability analyses, and related safety documents using NLP techniques.

## Getting Started

_Coming soon._

## License

This project is currently unlicensed. A license will be added in a future update.

---

# ResiliNER backend

Member 1's API gateway: FastAPI + PostgreSQL/PostGIS + Redis.

## Run it

```bash
docker compose up --build
```

Then open http://localhost:8000/docs — every endpoint is listed there and
you can test it directly in the browser, no separate tools needed.

## What's real vs what's still a stub

**Real right now:**
- `POST /telemetry` — writes sensor readings to Postgres, upserts the
  sensor's PostGIS location
- `POST /reports` — writes crowdsourced reports to Postgres with a real
  PostGIS point
- `GET /risk-state` — reads from Redis first, falls back to Postgres on a
  cache miss, repopulates the cache
- `POST /rules-result`, `POST /ml-result` — update a zone's risk using the
  dual-engine logic (physics floor overrides ML) in `app/services/risk_engine.py`

**Still a stub, waiting on the other members:**
- `POST /isolation-result` — accepts Member 3's isolation-twin output but
  doesn't yet insert per-village rows into `isolation_events`, since that
  needs Member 3 to send which specific villages were affected, not just a
  count. See the TODO in `app/routers/villages.py`.

## Testing the Redis fallback

```bash
docker compose stop redis
curl http://localhost:8000/risk-state   # should still return real data, just slower
docker compose start redis
```

## Project layout

```
app/
  main.py           # creates the app, includes every router
  database.py        # Postgres connection
  redis_client.py     # Redis connection
  routers/
    telemetry.py      # Member 4
    risk.py            # Member 2 + Member 3 + Member 5
    reports.py          # Member 6
    villages.py          # Member 3's isolation output
  models/schemas.py      # Pydantic models — the enforced data contracts
  services/risk_engine.py # physics-floor-vs-ML decision logic
init.sql                   # schema, auto-run on first container start
```
