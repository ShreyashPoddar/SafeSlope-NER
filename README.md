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

## Authorization

There are two separate, deliberately different mechanisms here — don't
mix them up.

**1. API key — for other members' services calling this gateway**

Write endpoints (`POST /telemetry`, `POST /reports`, `POST /rules-result`,
`POST /ml-result`, `POST /isolation-result`, `POST /risk-zones`,
`POST /villages`) require:
```
X-API-Key: <value of SERVICE_API_KEY>
```
This is for machine-to-machine calls — Member 2's rules engine, Member
4's hardware, Member 6's bot. No human login involved.

**2. Google Sign-In + session token — for real people using the dashboard**

Read endpoints (`GET /risk-state`, `/risk-zones`, `/villages`,
`/villages/isolated`, `/reports`, `/telemetry/sensors`,
`/telemetry/{sensor_id}`) require:
```
Authorization: Bearer <session token>
```

To get that token:
1. The dashboard shows Google's "Sign in with Google" button (Google
   Identity Services JS library) and gets back an ID token when someone
   logs in.
2. The dashboard `POST`s that ID token to `/auth/google` here.
3. This backend verifies it's genuinely from Google, looks up or creates
   a row in the `users` table, and returns a session token (a JWT, valid
   12 hours).
4. The dashboard sends that session token as the `Authorization` header
   on every subsequent request.

**Setup you need to do before this actually works:**
1. In Google Cloud Console, create an OAuth 2.0 Client ID (APIs &
   Services → Credentials → Create Credentials → OAuth client ID → Web
   application).
2. Add the dashboard's URL (e.g. `http://localhost:3000` for local dev)
   under "Authorized JavaScript origins."
3. Copy the generated Client ID into `GOOGLE_CLIENT_ID` in
   `docker-compose.yml`, replacing the placeholder.
4. Set a real random value for `JWT_SECRET` too — this is what protects
   your own session tokens from being forged.

`GET /auth/me` is a quick way to check whether a session token is still
valid — the dashboard can call it on load to see if someone's already
logged in.

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
