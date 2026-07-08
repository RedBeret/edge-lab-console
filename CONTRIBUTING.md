# Contributing to EdgeLab Console

## Dev setup

**Prerequisites:** Python 3.12+, Node.js 22+, npm

```bash
git clone https://github.com/RedBeret/edge-lab-console.git
cd edge-lab-console

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev   # Vite dev server at http://localhost:5173
```

The Vite dev server proxies `/api` and `/ws` traffic to `http://127.0.0.1:8000`.

## Commands

```bash
# Backend
python -m unittest discover -s backend/tests -v   # run tests
python -m compileall backend/app                  # syntax check

# Frontend
npm run build    # type-check + production build → dist/
npm run preview  # serve the dist/ build locally
```

## Project layout

```
backend/
├── app/
│   ├── main.py    # FastAPI app, routes, WebSocket handler
│   └── store.py   # In-memory synthetic data store
└── tests/
    └── test_api.py

frontend/
├── src/
│   ├── components/    # React UI components
│   ├── pages/         # Page-level components
│   └── types/         # Shared TypeScript types
└── vite.config.ts     # Proxy config for /api and /ws
```

## Pull request guidelines

- Branch from `main`, use `feat/`, `fix/`, or `chore/` prefix
- Backend: add a test in `backend/tests/test_api.py` for new endpoints
- Frontend: `npm run build` must pass before opening a PR
- No AI attribution in commits
