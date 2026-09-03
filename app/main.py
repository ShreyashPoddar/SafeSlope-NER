import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import database
from app.routers import telemetry, risk, reports, villages, auth

app = FastAPI(title="SafeSlope-NER API")

# Permissive for the hackathon so Member 5's dashboard (running on a
# different port) can call this API from the browser. Tighten
# allow_origins to the dashboard's real URL before anything public-facing.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    # Postgres takes a few extra seconds on first boot to run init.sql.
    # Retry instead of crashing outright, so nobody has to manually
    # restart the api container the way we just did.
    max_attempts = 10
    for attempt in range(1, max_attempts + 1):
        try:
            await database.connect()
            print("Connected to Postgres.")
            break
        except Exception as exc:
            if attempt == max_attempts:
                raise
            print(f"Postgres not ready yet (attempt {attempt}/{max_attempts}): {exc}")
            await asyncio.sleep(2)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
def read_root():
    return {"status": "SafeSlope-NER API running"}


app.include_router(telemetry.router)
app.include_router(risk.router)
app.include_router(reports.router)
app.include_router(villages.router)
app.include_router(auth.router)
