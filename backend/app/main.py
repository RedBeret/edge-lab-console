from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .store import add_note, fetch_dashboard, fetch_run_detail, fetch_runs, initialize_database


class NotePayload(BaseModel):
    author: str = Field(min_length=2, max_length=60)
    content: str = Field(min_length=3, max_length=500)


app = FastAPI(
    title="EdgeLab Console API",
    version="0.1.0",
    description="Backend API for a full-stack lab operations and telemetry console.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/dashboard")
def dashboard() -> dict:
    return fetch_dashboard()


@app.get("/api/runs")
def runs(
    search: str = Query(default="", max_length=80),
    status: str = Query(default="", max_length=40),
    environment: str = Query(default="", max_length=80),
    owner: str = Query(default="", max_length=80),
) -> list[dict]:
    return fetch_runs(
        search=search.strip(),
        status=status.strip(),
        environment=environment.strip(),
        owner=owner.strip(),
    )


@app.get("/api/runs/{run_id}")
def run_detail(run_id: str) -> dict:
    detail = fetch_run_detail(run_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return detail


@app.post("/api/runs/{run_id}/notes")
def create_note(run_id: str, payload: NotePayload) -> dict:
    detail = fetch_run_detail(run_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Run not found")

    created_at = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    note = add_note(
        run_id=run_id,
        author=payload.author.strip(),
        content=payload.content.strip(),
        created_at=created_at,
    )
    return {"note": note}


@app.websocket("/ws/runs/{run_id}")
async def run_signal_stream(websocket: WebSocket, run_id: str) -> None:
    detail = fetch_run_detail(run_id)
    if detail is None:
        await websocket.close(code=4404)
        return

    await websocket.accept()

    snapshots = {
        "EL-2401": [
            {"level": "watch", "message": "Recovery window widened after sustained load.", "timestamp": "10:27"},
            {"level": "alert", "message": "Thermal drift still above baseline by 4C.", "timestamp": "10:28"},
            {"level": "note", "message": "Queueing comparison against last stable pass.", "timestamp": "10:29"},
        ],
        "EL-2402": [
            {"level": "ok", "message": "Regression pack remains clean.", "timestamp": "10:12"},
            {"level": "ok", "message": "RF throughput variance stayed inside target.", "timestamp": "10:13"},
            {"level": "note", "message": "Run can be handed off without extra triage.", "timestamp": "10:14"},
        ],
        "EL-2403": [
            {"level": "watch", "message": "Latency jitter rose during the long-duration segment.", "timestamp": "10:01"},
            {"level": "watch", "message": "Batch-size change is the likely cause.", "timestamp": "10:02"},
            {"level": "note", "message": "Recommend retest with baseline batch size.", "timestamp": "10:03"},
        ],
        "EL-2404": [
            {"level": "alert", "message": "Validated boot profile still not restored.", "timestamp": "09:43"},
            {"level": "alert", "message": "Artifact bundle remains missing.", "timestamp": "09:44"},
            {"level": "note", "message": "Keep rack blocked until baseline image is reapplied.", "timestamp": "09:45"},
        ],
    }

    try:
        for item in snapshots.get(run_id, []):
            await websocket.send_json(item)
            await asyncio.sleep(1.0)

        while True:
            await websocket.send_json(
                {
                    "level": "heartbeat",
                    "message": f"{detail['name']} is still streaming telemetry.",
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                }
            )
            await asyncio.sleep(4.0)
    except WebSocketDisconnect:
        return
