# EdgeLab Console

EdgeLab Console is a lab operations tool for tracking device test runs, surfacing config drift, managing artifacts, and keeping a live operator log for each run.

It is built for the moment when a rack is hot, a run is in progress, and you need to know fast: what is the pass rate, what triggered alerts, and has the config drifted from baseline.

## What it does

The dashboard shows active runs, overall pass rate, and open alerts across the rack. The run queue is filterable by search term, status, environment, or owner. Select any run to see the full detail panel: config diffs from baseline, artifact list, alert feed, operator notes, and an event timeline.

A WebSocket endpoint streams live telemetry snapshots per run. As signals come in during a run, they appear in the event rail. You can also post notes directly against a run.

## How a session works

Operator opens the dashboard. The rack has four active runs. EL-2404 is showing red. She selects it and sees two config drift items: the boot profile has not been restored from the last known good state, and the artifact bundle did not generate. Two alerts are open. She posts a note: "baseline image needs to be reapplied before this rack unblocks." That note shows up in the run detail and the handoff summary.

## API design

The backend exposes:

- `GET /api/dashboard` - metrics and open alerts
- `GET /api/runs?search=&status=&environment=&owner=` - filterable run list
- `GET /api/runs/{run_id}` - full run detail including diffs, artifacts, alerts, notes, and events
- `POST /api/runs/{run_id}/notes` - add an operator note to a run
- `WS /ws/runs/{run_id}` - live telemetry stream

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies API traffic to `http://127.0.0.1:8000`.

## Verification

- `python -m unittest discover -s backend/tests -v`
- `python -m compileall backend/app`
- `npm run build`
