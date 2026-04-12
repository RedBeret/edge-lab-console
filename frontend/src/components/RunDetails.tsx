import type { RunDetail, SignalMessage } from "../types";

interface RunDetailsProps {
  detail: RunDetail | null;
  signalMessages: SignalMessage[];
  noteDraft: string;
  noteAuthor: string;
  onNoteDraftChange: (value: string) => void;
  onNoteAuthorChange: (value: string) => void;
  onSubmitNote: () => void;
  isSavingNote: boolean;
}

export function RunDetails({
  detail,
  signalMessages,
  noteDraft,
  noteAuthor,
  onNoteDraftChange,
  onNoteAuthorChange,
  onSubmitNote,
  isSavingNote,
}: RunDetailsProps) {
  if (!detail) {
    return (
      <section className="run-detail">
        <p className="empty-state">Pick a run to inspect details.</p>
      </section>
    );
  }

  return (
    <section className="run-detail">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Selected run</p>
          <h2>{detail.name}</h2>
        </div>
        <span className={`status-badge status-badge--${normalizeStatus(detail.status)}`}>
          {detail.status}
        </span>
      </div>

      <div className="run-detail__hero">
        <div>
          <p className="run-detail__summary">{detail.summary}</p>
          <div className="run-detail__chips">
            <span>{detail.environment}</span>
            <span>{detail.platform}</span>
            <span>{detail.owner}</span>
            <span>{detail.duration_minutes} min</span>
          </div>
        </div>
        <div className="run-detail__health">
          <strong>{detail.pass_rate}%</strong>
          <span>Current pass rate</span>
        </div>
      </div>

      <div className="run-detail__grid">
        <article className="detail-card">
          <h3>Config drift</h3>
          <div className="diff-list">
            {detail.configDiffs.map((diff) => (
              <div key={diff.id} className="diff-item">
                <div className="diff-item__top">
                  <strong>{diff.key}</strong>
                  <span>{diff.baseline} → {diff.observed}</span>
                </div>
                <p>{diff.impact}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="detail-card">
          <h3>Artifacts</h3>
          <div className="artifact-list">
            {detail.artifacts.map((artifact) => (
              <div key={artifact.id} className="artifact-item">
                <div>
                  <strong>{artifact.name}</strong>
                  <p>{artifact.kind}</p>
                </div>
                <div className="artifact-item__meta">
                  <span>{artifact.size}</span>
                  <span className={`artifact-status artifact-status--${artifact.status}`}>
                    {artifact.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="detail-card">
          <h3>Notes</h3>
          <div className="note-form">
            <input
              type="text"
              value={noteAuthor}
              onChange={(event) => onNoteAuthorChange(event.target.value)}
              placeholder="Author"
            />
            <textarea
              value={noteDraft}
              onChange={(event) => onNoteDraftChange(event.target.value)}
              placeholder="Add a quick handoff or triage note..."
            />
            <button type="button" onClick={onSubmitNote} disabled={isSavingNote}>
              {isSavingNote ? "Saving..." : "Add note"}
            </button>
          </div>
          <div className="note-list">
            {detail.notes.map((note) => (
              <div key={note.id} className="note-item">
                <div className="note-item__top">
                  <strong>{note.author}</strong>
                  <span>{formatDate(note.created_at)}</span>
                </div>
                <p>{note.content}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="detail-card">
          <h3>Timeline</h3>
          <div className="timeline-list">
            {detail.events.map((event) => (
              <div key={event.id} className={`timeline-item timeline-item--${event.type}`}>
                <div className="timeline-item__top">
                  <strong>{event.type}</strong>
                  <span>{formatDate(event.timestamp)}</span>
                </div>
                <p>{event.message}</p>
              </div>
            ))}
          </div>
        </article>
      </div>

      <article className="detail-card detail-card--full">
        <h3>Live signal rail</h3>
        <div className="signal-inline">
          {signalMessages.length ? (
            signalMessages.map((message, index) => (
              <div key={`${message.timestamp}-${index}`} className={`signal-item signal-item--${message.level}`}>
                <div className="signal-item__top">
                  <strong>{message.level}</strong>
                  <span>{message.timestamp}</span>
                </div>
                <p>{message.message}</p>
              </div>
            ))
          ) : (
            <p className="empty-state">Waiting for signal updates...</p>
          )}
        </div>
      </article>
    </section>
  );
}

function formatDate(value: string) {
  return new Date(value).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function normalizeStatus(status: string) {
  return status.toLowerCase().replace(/\s+/g, "-");
}
