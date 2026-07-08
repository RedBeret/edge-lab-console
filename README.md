# EdgeLab Console

[![CI](https://github.com/RedBeret/edge-lab-console/actions/workflows/ci.yml/badge.svg)](https://github.com/RedBeret/edge-lab-console/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-green)

EdgeLab Console is a lab operations tool for tracking device test runs, surfacing config drift, managing artifacts, and keeping a live operator log for each run.

It is built for the moment when a rack is hot, a run is in progress, and you need to know fast: what is the pass rate, what triggered alerts, and has the config drifted from baseline.

## Architecture

```mermaid
graph LR
    subgraph frontend["Frontend (React 19 + Vite)"]
        DB[Dashboard\npass rate · alerts]
        RQ[Run Queue\nfilter by status / env]
        RD[Run Detail\ndiffs · artifacts · notes · timeline]
    end

    subgraph backend["Backend (FastAPI)"]
        API[REST API\n/api/dashboard\n/api/runs]
        WS[WebSocket\n/ws/runs/{id}]
        ST[(In-memory store\nsynthetic runs)]
    end

    DB -->|GET /api/dashboard| API
    RQ -->|GET /api/runs| API
    RD -->|GET /api/runs/{id}| API
    RD -->|POST notes| API
    RD <-->|live telemetry| WS
    API --> ST
    WS --> ST
```

## Case Study: Blocking Config Drift in a Four-Run Rack Session

**Problem.** A lab rack is running four simultaneous firmware validation runs.
Run EL-2404 goes red 14 minutes in. The on-shift operator needs to determine
in under two minutes whether to abort the other three runs or let them continue —
aborting wastes four hours of setup time; letting a bad config propagate means
starting the entire set over.

**Constraints.** The rack is shared with two other teams. The operator cannot
reboot or reconfigure without team-lead sign-off. The live telemetry feed drops
connection every ~90 seconds (known infra limitation). Operator notes must be
preserved across reconnects for handoff.

**Architecture.** The EdgeLab Console approach:

1. The Dashboard shows all four runs' pass rates and open alerts in a single view — the operator sees EL-2404 is at 23% pass rate with two open alerts in under five seconds.
2. Selecting EL-2404 opens the Run Detail panel. The config diff section shows two drift items: boot profile not restored from last-known-good, artifact bundle did not generate.
3. The WebSocket stream auto-reconnects on drop. Events that arrive during a disconnect are replayed from the store on reconnect — no telemetry gaps.
4. The operator posts a note: *"baseline image needs reapplied before this rack unblocks."* The note persists in the run record and appears in the handoff summary.

**Trade-offs.** In-memory store means data is lost on server restart — acceptable for a lab session tool where the run source of truth is the upstream test framework. A SQLite backend would add persistence at the cost of setup complexity that the target environment (developer laptop, CI runner) doesn't justify.

**Results.**

| Metric | Outcome |
|--------|---------|
| Time to root-cause EL-2404 | Under 2 minutes |
| Other three runs aborted? | No — drift was isolated to EL-2404 |
| Operator note visible in next-shift handoff | Yes |
| WebSocket reconnect loss | 0 events (replay on reconnect) |

All data is synthetic.

## Quick Start

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

**Windows (one command):**

```bat
run.bat
```

## Air-Gapped / Offline Install

```bash
# On internet-connected machine — download backend wheels
pip download -r backend/requirements.txt -d ./wheels --python-version 3.12

# Download frontend packages (produces node_modules.tar.gz equivalent)
cd frontend && npm pack --dry-run   # or use npm ci --prefer-offline after copying node_modules

# Transfer wheels/ and frontend/node_modules/ to target host
pip install --no-index --find-links ./wheels -r backend/requirements.txt
# frontend: node_modules is already present — npm run build works offline
```

The app runs entirely on `localhost` — no outbound connections required after install.

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/dashboard` | Metrics and open alerts |
| `GET` | `/api/runs` | Filterable run list (`?search=&status=&environment=&owner=`) |
| `GET` | `/api/runs/{run_id}` | Full run detail: diffs, artifacts, alerts, notes, events |
| `POST` | `/api/runs/{run_id}/notes` | Add an operator note |
| `WS` | `/ws/runs/{run_id}` | Live telemetry stream |

## Verification

```bash
python -m unittest discover -s backend/tests -v
python -m compileall backend/app
cd frontend && npm run build
```

## Stack

Python 3.12 · FastAPI · Uvicorn · React 19 · TypeScript · Vite

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
