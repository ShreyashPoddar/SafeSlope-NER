// SafeSlope-NER backend API client
// Drop this file into your React project (e.g. src/api.js) and import
// the functions you need. No other setup required beyond filling in
// BASE_URL below.

// ---------------------------------------------------------------
// 1. SET THIS to wherever the backend is currently reachable.
//    Ask Member 1 for the current value if you're not sure —
//    it changes depending on whether it's running locally, through
//    ngrok, or (eventually) deployed permanently.
// ---------------------------------------------------------------
const BASE_URL = "https://judge-alkaline-eloquence.ngrok-free.dev";

// Required only when BASE_URL is an ngrok tunnel — without this header,
// ngrok's free tier shows an HTML warning page instead of your actual
// API response. Harmless to always include it.
const EXTRA_HEADERS = { "ngrok-skip-browser-warning": "true" };

function authHeaders(token) {
  return { ...EXTRA_HEADERS, Authorization: `Bearer ${token}` };
}

async function handle(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

// ---------------------------------------------------------------
// AUTH
// ---------------------------------------------------------------

// Call this when the user clicks "Sign in with GitHub". It navigates
// the whole page away (not a popup) to GitHub's login screen, then
// GitHub sends them back to /auth/callback?token=... on YOUR app —
// see the note at the bottom of this file for how to handle that route.
export function loginWithGithub() {
  window.location.href = `${BASE_URL}/auth/github/login`;
}

// Checks whether a session token is still valid, and returns the
// logged-in user's info if so. Throws if the token is invalid/expired.
export async function getCurrentUser(token) {
  const res = await fetch(`${BASE_URL}/auth/me`, {
    headers: authHeaders(token),
  });
  return handle(res);
}

// ---------------------------------------------------------------
// READS — all of these require a valid session token
// ---------------------------------------------------------------

export async function getRiskState(token) {
  const res = await fetch(`${BASE_URL}/risk-state`, {
    headers: authHeaders(token),
  });
  return handle(res);
}

export async function getRiskZones(token) {
  const res = await fetch(`${BASE_URL}/risk-zones`, {
    headers: authHeaders(token),
  });
  return handle(res);
}

export async function getVillages(token) {
  const res = await fetch(`${BASE_URL}/villages`, {
    headers: authHeaders(token),
  });
  return handle(res);
}

export async function getIsolatedVillages(token) {
  const res = await fetch(`${BASE_URL}/villages/isolated`, {
    headers: authHeaders(token),
  });
  return handle(res);
}

export async function getReports(token) {
  const res = await fetch(`${BASE_URL}/reports/`, {
    headers: authHeaders(token),
  });
  return handle(res);
}

export async function getSensors(token) {
  const res = await fetch(`${BASE_URL}/telemetry/sensors`, {
    headers: authHeaders(token),
  });
  return handle(res);
}

// ---------------------------------------------------------------
// HOW TO HANDLE THE LOGIN REDIRECT IN YOUR REACT APP
// ---------------------------------------------------------------
// You need a route at /auth/callback that reads the token from the
// URL and stores it (in React state/context — most React routers
// give you this via useSearchParams or similar). Example with
// react-router-dom:
//
//   import { useSearchParams, useNavigate } from "react-router-dom";
//   import { useEffect } from "react";
//
//   function AuthCallback({ onLogin }) {
//     const [params] = useSearchParams();
//     const navigate = useNavigate();
//
//     useEffect(() => {
//       const token = params.get("token");
//       const error = params.get("error");
//       if (token) {
//         onLogin(token);       // save it in your app's state
//         navigate("/dashboard");
//       } else if (error) {
//         navigate("/login?error=" + error);
//       }
//     }, []);
//
//     return <p>Signing you in...</p>;
//   }
