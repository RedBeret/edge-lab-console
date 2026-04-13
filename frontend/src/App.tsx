import { startTransition, useDeferredValue, useEffect, useMemo, useState } from "react";
import { SummaryGrid } from "./components/SummaryGrid";
import { RunTable } from "./components/RunTable";
import { RunDetails } from "./components/RunDetails";
import type { DashboardData, RunDetail, RunSummary, SignalMessage } from "./types";
import "./styles.css";

const STATUS_OPTIONS = ["All", "Healthy", "Warning", "Investigating", "Blocked"];

export default function App() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [selectedRun, setSelectedRun] = useState<RunDetail | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [environmentFilter, setEnvironmentFilter] = useState("All");
  const [ownerFilter, setOwnerFilter] = useState("All");
  const [signalMessages, setSignalMessages] = useState<SignalMessage[]>([]);
  const [noteDraft, setNoteDraft] = useState("");
  const [noteAuthor, setNoteAuthor] = useState("Steven");
  const [loadingRuns, setLoadingRuns] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [savingNote, setSavingNote] = useState(false);
  const [error, setError] = useState("");

  const deferredSearch = useDeferredValue(search);

  useEffect(() => {
    void fetchJson<DashboardData>("/api/dashboard")
      .then(setDashboard)
      .catch(() => setError("Could not load dashboard data."));
  }, []);

  useEffect(() => {
    setLoadingRuns(true);
    const params = new URLSearchParams();

    if (deferredSearch.trim()) {
      params.set("search", deferredSearch.trim());
    }
    if (statusFilter !== "All") {
      params.set("status", statusFilter);
    }
    if (environmentFilter !== "All") {
      params.set("environment", environmentFilter);
    }
    if (ownerFilter !== "All") {
      params.set("owner", ownerFilter);
    }

    void fetchJson<RunSummary[]>(`/api/runs?${params.toString()}`)
      .then((data) => {
        setRuns(data);
        startTransition(() => {
          if (!data.length) {
            setSelectedRunId(null);
            setSelectedRun(null);
            return;
          }

          const stillVisible = data.some((run) => run.id === selectedRunId);
          if (!stillVisible) {
            setSelectedRunId(data[0].id);
          }
        });
      })
      .catch(() => setError("Could not load runs."))
      .finally(() => setLoadingRuns(false));
  }, [deferredSearch, statusFilter, environmentFilter, ownerFilter, selectedRunId]);

  useEffect(() => {
    if (!selectedRunId) {
      return;
    }

    setLoadingDetail(true);
    void fetchJson<RunDetail>(`/api/runs/${selectedRunId}`)
      .then((data) => setSelectedRun(data))
      .catch(() => setError("Could not load the selected run."))
      .finally(() => setLoadingDetail(false));
  }, [selectedRunId]);

  useEffect(() => {
    if (!selectedRunId) {
      setSignalMessages([]);
      return;
    }

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws/runs/${selectedRunId}`);

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data) as SignalMessage;
      setSignalMessages((current) => [payload, ...current].slice(0, 8));
    };

    socket.onerror = () => {
      setSignalMessages([]);
    };

    return () => socket.close();
  }, [selectedRunId]);

  const environments = useMemo(
    () => ["All", ...new Set(runs.map((run) => run.environment))],
    [runs]
  );

  const owners = useMemo(
    () => ["All", ...new Set(runs.map((run) => run.owner))],
    [runs]
  );

  const selectedSummary = runs.find((run) => run.id === selectedRunId);

  const submitNote = async () => {
    if (!selectedRunId || !noteDraft.trim() || !noteAuthor.trim()) {
      return;
    }

    setSavingNote(true);
    try {
      await fetchJson(`/api/runs/${selectedRunId}/notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          author: noteAuthor.trim(),
          content: noteDraft.trim()
        })
      });

      setNoteDraft("");
      const refreshed = await fetchJson<RunDetail>(`/api/runs/${selectedRunId}`);
      setSelectedRun(refreshed);
    } catch {
      setError("Could not save the note.");
    } finally {
      setSavingNote(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="hero-shell">
        <div className="hero-copy">
          <p className="hero-kicker">Full-stack internal tooling showcase</p>
          <h1>EdgeLab Console</h1>
          <p className="hero-description">
            A lab operations console for tracking device runs, artifacts, config drift, and live signal updates.
          </p>
          <div className="hero-proof">
            <span>React + TypeScript frontend</span>
            <span>FastAPI + SQLite backend</span>
            <span>Operational UX over noisy technical data</span>
          </div>
        </div>
        <aside className="hero-sidecard">
          <p className="panel-kicker">Why this project works</p>
          <h2>Believable product, not generic CRUD</h2>
          <p>
            Built to feel like something a platform, device, or validation team could actually use day to day.
          </p>
          <div className="hero-sidecard__footer">
            <span>{selectedSummary?.id ?? "EL-2401"}</span>
            <span>{selectedSummary?.status ?? "Investigating"}</span>
          </div>
        </aside>
      </header>

      <main className="content-shell">
        <SummaryGrid dashboard={dashboard} />

        <section className="controls-panel">
          <div className="controls-panel__top">
            <div>
              <p className="panel-kicker">Filters</p>
              <h2>Find the run that needs attention</h2>
            </div>
            {error ? <p className="error-banner">{error}</p> : null}
          </div>

          <div className="controls-grid">
            <label>
              Search
              <div className="search-wrap">
                <input
                  type="search"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Search by run, platform, or summary"
                />
                {search ? (
                  <button
                    className="search-clear"
                    onClick={() => setSearch("")}
                    type="button"
                    aria-label="Clear search"
                  >
                    ×
                  </button>
                ) : null}
              </div>
            </label>

            <label>
              Status
              <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
                {STATUS_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Environment
              <select
                value={environmentFilter}
                onChange={(event) => setEnvironmentFilter(event.target.value)}
              >
                {environments.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Owner
              <select value={ownerFilter} onChange={(event) => setOwnerFilter(event.target.value)}>
                {owners.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </section>

        <section className="workspace-grid">
          <div className="workspace-grid__left">
            {loadingRuns ? <p className="loading-state">Loading runs...</p> : null}
            <RunTable
              runs={runs}
              selectedRunId={selectedRunId}
              onSelect={(runId) => setSelectedRunId(runId)}
            />
          </div>

          <div className="workspace-grid__right">
            {loadingDetail ? <p className="loading-state">Loading run details...</p> : null}
            <RunDetails
              detail={selectedRun}
              signalMessages={signalMessages}
              noteDraft={noteDraft}
              noteAuthor={noteAuthor}
              onNoteDraftChange={setNoteDraft}
              onNoteAuthorChange={setNoteAuthor}
              onSubmitNote={submitNote}
              isSavingNote={savingNote}
            />
          </div>
        </section>
      </main>
    </div>
  );
}

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}
