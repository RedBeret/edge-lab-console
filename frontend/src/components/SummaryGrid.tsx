import type { DashboardData } from "../types";

interface SummaryGridProps {
  dashboard: DashboardData | null;
}

export function SummaryGrid({ dashboard }: SummaryGridProps) {
  if (!dashboard) {
    return null;
  }

  return (
    <section className="summary-grid">
      <div className="metric-grid">
        {dashboard.metrics.map((metric) => (
          <article key={metric.label} className={`metric-card metric-card--${metric.tone}`}>
            <p className="metric-card__label">{metric.label}</p>
            <strong className="metric-card__value">{metric.value}</strong>
            <p className="metric-card__helper">{metric.helper}</p>
          </article>
        ))}
      </div>

      <aside className="alert-stack">
        <div className="panel-header">
          <div>
            <p className="panel-kicker">Attention queue</p>
            <h2>Recent alerts</h2>
          </div>
        </div>
        <div className="alert-stack__list">
          {dashboard.alerts.map((alert) => (
            <div key={alert.id} className={`alert-card alert-card--${alert.severity}`}>
              <div className="alert-card__top">
                <span>{alert.run_id}</span>
                <span>{formatTime(alert.created_at)}</span>
              </div>
              <strong>{alert.title}</strong>
              <p>{alert.detail}</p>
            </div>
          ))}
        </div>
      </aside>
    </section>
  );
}

function formatTime(value: string) {
  return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
