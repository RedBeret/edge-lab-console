import type { RunSummary } from "../types";

interface RunTableProps {
  runs: RunSummary[];
  selectedRunId: string | null;
  onSelect: (runId: string) => void;
}

export function RunTable({ runs, selectedRunId, onSelect }: RunTableProps) {
  return (
    <section className="run-board">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Run queue</p>
          <h2>Active work</h2>
        </div>
        <span className="run-board__count">{runs.length} runs</span>
      </div>

      <div className="run-board__list">
        {runs.map((run) => (
          <button
            type="button"
            key={run.id}
            className={`run-row ${selectedRunId === run.id ? "run-row--selected" : ""}`}
            onClick={() => onSelect(run.id)}
          >
            <div className="run-row__top">
              <div>
                <p className="run-row__id">{run.id}</p>
                <h3>{run.name}</h3>
              </div>
              <span className={`status-badge status-badge--${normalizeStatus(run.status)}`}>
                {run.status}
              </span>
            </div>
            <p className="run-row__summary">{run.summary}</p>
            <div className="run-row__meta">
              <span>{run.environment}</span>
              <span>{run.platform}</span>
              <span>{run.owner}</span>
            </div>
            <div className="run-row__stats">
              <span>{run.pass_rate}% pass</span>
              <span>{run.anomalies} anomalies</span>
              <span>{run.devices} devices</span>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}

function normalizeStatus(status: string) {
  return status.toLowerCase().replace(/\s+/g, "-");
}
