# Connecting the dashboard to the backend

This is everything you need to wire the React dashboard up to the
ResiliNER/SafeSlope-NER backend, without needing to ask Member 1
directly. If something here doesn't match what you're seeing, check
the "Troubleshooting" section at the bottom first.

## 1. Get the current base URL

The backend isn't deployed permanently yet — it's running on Member 1's
laptop through a tunnel. Ask for the current URL if it's not this one:

```
https://judge-alkaline-eloquence.ngrok-free.dev
```

Test it's alive right now by opening `<that URL>/docs` in your browser —
if you see a full API documentation page, it's up. If you get a
connection error, the backend isn't currently running and you'll need
to wait or ping Member 1.

## 2. Use the ready-made API client

`frontend-api-client.js` (in this repo) has every function you need
already written — copy it into your project (e.g. `src/api.js`) and
update the `BASE_URL` constant at the top if it's changed. It has
functions like `getRiskState(token)`, `getVillages(token)`, etc. — call
them, they return parsed JSON directly.

## 3. Login flow — how it actually works

This is **not** a popup or an API call you make directly — it's a full
page redirect, the same way "Sign in with Google" works on most sites:

1. User clicks your "Sign in with GitHub" button
2. Your code calls `loginWithGithub()` from the API client — this
   navigates the whole browser tab to GitHub's login page
3. User approves on GitHub's site
4. GitHub sends them back to the **backend**, which then redirects them
   to **your app** at `/auth/callback?token=<a long token>`
5. Your app needs a route at `/auth/callback` that reads that token from
   the URL and saves it (see the example in `frontend-api-client.js`)
6. From then on, pass that token into every API call (`getRiskState(token)`,
   etc.) — it proves who's logged in

**You need a route at `/auth/callback` in your app for this to work at
all** — without it, the redirect has nowhere valid to land.

## 4. Every available endpoint

| What it gives you | Function to call | Needs login? |
|---|---|---|
| Current risk state for all zones | `getRiskState(token)` | Yes |
| List of all risk zones | `getRiskZones(token)` | Yes |
| List of all registered villages | `getVillages(token)` | Yes |
| Villages currently cut off | `getIsolatedVillages(token)` | Yes |
| Crowdsourced reports | `getReports(token)` | Yes |
| Registered sensors | `getSensors(token)` | Yes |
| Who's currently logged in | `getCurrentUser(token)` | Yes |

Everything requires a valid token from step 3 — there's no public,
unauthenticated read access currently.

## 5. What the data actually looks like

Example response from `getRiskState(token)`:
```json
{
  "zone_1": {
    "id": 1,
    "zone_name": "zone_1",
    "current_risk": "LOW",
    "ml_risk_pct": 12.0,
    "ml_confidence_pct": 60.0,
    "updated_at": "2026-09-03T06:49:39"
  },
  "zone_2": { "...": "same shape" }
}
```
`current_risk` is always one of `"LOW"`, `"MODERATE"`, or `"HIGH"` — safe
to use directly for color-coding your risk map.

## 6. Troubleshooting

**"Failed to fetch" / network error in the browser console**
The backend isn't currently running, or the URL in `BASE_URL` is stale.
Check `<BASE_URL>/docs` loads directly in a browser tab first — if that
fails too, it's not you, the backend itself is down.

**You get an HTML page instead of JSON**
This is ngrok's free-tier warning page. Make sure `EXTRA_HEADERS` (the
`ngrok-skip-browser-warning` header) is actually being sent — it's
already baked into every function in `frontend-api-client.js`, so this
should only happen if you're calling `fetch` directly instead of using
the provided functions.

**401 "Invalid or expired session"**
Your token is either wrong or has expired (they last 12 hours). Have the
user log in again via `loginWithGithub()`.

**CORS errors in the console**
This shouldn't happen — the backend already allows requests from any
origin. If you see one anyway, double-check `BASE_URL` doesn't have a
typo (e.g. `http` vs `https`, or a trailing slash where one doesn't
belong).

**The redirect after login goes to the backend's URL, not your app**
This means `FRONTEND_URL` isn't set correctly on the backend's `.env` —
it needs to match wherever your dashboard is actually running (e.g.
`http://localhost:3000`). This is a backend-side config, not something
fixable from your side — flag it if it happens.
