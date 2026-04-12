export interface Metric {
  label: string;
  value: string;
  helper: string;
  tone: "neutral" | "positive" | "warning";
}

export interface AlertItem {
  id: number;
  run_id?: string;
  severity: string;
  title: string;
  detail: string;
  created_at: string;
}

export interface RunSummary {
  id: string;
  name: string;
  environment: string;
  platform: string;
  owner: string;
  status: string;
  started_at: string;
  updated_at: string;
  duration_minutes: number;
  pass_rate: number;
  anomalies: number;
  devices: number;
  summary: string;
}

export interface Artifact {
  id: number;
  kind: string;
  name: string;
  size: string;
  status: string;
}

export interface ConfigDiff {
  id: number;
  key: string;
  baseline: string;
  observed: string;
  impact: string;
}

export interface NoteItem {
  id: number;
  author: string;
  content: string;
  created_at: string;
}

export interface EventItem {
  id: number;
  timestamp: string;
  type: string;
  message: string;
}

export interface RunDetail extends RunSummary {
  alerts: AlertItem[];
  artifacts: Artifact[];
  configDiffs: ConfigDiff[];
  notes: NoteItem[];
  events: EventItem[];
}

export interface DashboardData {
  metrics: Metric[];
  alerts: AlertItem[];
}

export interface SignalMessage {
  level: string;
  message: string;
  timestamp: string;
}
