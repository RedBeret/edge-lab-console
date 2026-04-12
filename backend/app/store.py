from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "edge_lab.db"


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with connect() as connection:
        cursor = connection.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                environment TEXT NOT NULL,
                platform TEXT NOT NULL,
                owner TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                pass_rate INTEGER NOT NULL,
                anomalies INTEGER NOT NULL,
                devices INTEGER NOT NULL,
                summary TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                name TEXT NOT NULL,
                size TEXT NOT NULL,
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                message TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS config_diffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                key TEXT NOT NULL,
                baseline TEXT NOT NULL,
                observed TEXT NOT NULL,
                impact TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                author TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )

        count = cursor.execute("SELECT COUNT(*) AS count FROM runs").fetchone()
        if count["count"]:
            return

        cursor.executemany(
            """
            INSERT INTO runs (
                id, name, environment, platform, owner, status,
                started_at, updated_at, duration_minutes, pass_rate,
                anomalies, devices, summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "EL-2401",
                    "Jetson Thermal Sweep",
                    "Edge Lab A",
                    "Jetson Orin Nano",
                    "Steven",
                    "Investigating",
                    "2026-04-12T07:10:00",
                    "2026-04-12T10:26:00",
                    196,
                    91,
                    3,
                    6,
                    "Thermal validation run with intermittent packet-loss spikes after sustained load.",
                ),
                (
                    "EL-2402",
                    "RF Bring-Up Regression",
                    "RF Bench",
                    "X65 Dev Kit",
                    "Mina",
                    "Healthy",
                    "2026-04-12T08:00:00",
                    "2026-04-12T10:11:00",
                    131,
                    98,
                    0,
                    4,
                    "Regression pack is trending clean with stable throughput and no critical alerts.",
                ),
                (
                    "EL-2403",
                    "Sensor Fusion Latency Check",
                    "Edge Lab B",
                    "XR2+ Board",
                    "Jordan",
                    "Warning",
                    "2026-04-12T06:45:00",
                    "2026-04-12T10:03:00",
                    198,
                    94,
                    2,
                    8,
                    "Latency budget is within range overall, but two runs drifted beyond baseline during long sessions.",
                ),
                (
                    "EL-2404",
                    "Power Cycle Validation",
                    "System Rack",
                    "Compute Module A3",
                    "Anika",
                    "Blocked",
                    "2026-04-12T05:50:00",
                    "2026-04-12T09:42:00",
                    232,
                    72,
                    6,
                    5,
                    "Validation blocked after repeated config mismatch on boot profile and one missing artifact bundle.",
                ),
            ],
        )

        cursor.executemany(
            """
            INSERT INTO alerts (run_id, severity, title, detail, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    "EL-2401",
                    "high",
                    "Thermal drift after sustained load",
                    "Temperature rose 6C above baseline after the twentieth iteration.",
                    "2026-04-12T10:23:00",
                ),
                (
                    "EL-2401",
                    "medium",
                    "Packet-loss burst detected",
                    "Three back-to-back bursts were observed while the device recovered from a frequency shift.",
                    "2026-04-12T10:14:00",
                ),
                (
                    "EL-2403",
                    "medium",
                    "Latency exceeded budget",
                    "Sensor fusion path crossed the 90 ms threshold twice during extended runtime.",
                    "2026-04-12T09:58:00",
                ),
                (
                    "EL-2404",
                    "high",
                    "Boot profile mismatch",
                    "Observed boot configuration does not match the validated baseline profile.",
                    "2026-04-12T09:40:00",
                ),
            ],
        )

        cursor.executemany(
            """
            INSERT INTO artifacts (run_id, kind, name, size, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ("EL-2401", "log bundle", "thermal-sweep-0426.zip", "18 MB", "ready"),
                ("EL-2401", "report", "packet-loss-summary.md", "12 KB", "ready"),
                ("EL-2402", "capture", "rf-regression-pcap.pcapng", "31 MB", "ready"),
                ("EL-2403", "report", "latency-budget-breakdown.csv", "88 KB", "ready"),
                ("EL-2404", "firmware", "boot-profile-diff.json", "6 KB", "missing"),
            ],
        )

        cursor.executemany(
            """
            INSERT INTO config_diffs (run_id, key, baseline, observed, impact)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    "EL-2401",
                    "network.recovery_window_ms",
                    "1200",
                    "1800",
                    "Longer recovery window lines up with the observed packet-loss burst.",
                ),
                (
                    "EL-2401",
                    "thermal.cooldown_threshold_c",
                    "72",
                    "76",
                    "Higher threshold likely delayed mitigation during the last phase of the run.",
                ),
                (
                    "EL-2403",
                    "sensor.pipeline.batch_size",
                    "16",
                    "24",
                    "Larger batch size improved throughput but added latency variance.",
                ),
                (
                    "EL-2404",
                    "boot.profile",
                    "validated-a3-edge",
                    "lab-a3-debug",
                    "Run is blocked until the rack is restored to the validated profile.",
                ),
            ],
        )

        cursor.executemany(
            """
            INSERT INTO events (run_id, timestamp, type, message)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("EL-2401", "2026-04-12T10:23:00", "alert", "Thermal drift crossed the watch threshold."),
                ("EL-2401", "2026-04-12T10:12:00", "telemetry", "Packet-loss burst detected during failover."),
                ("EL-2401", "2026-04-12T09:48:00", "checkpoint", "Sustained load stage started."),
                ("EL-2402", "2026-04-12T10:11:00", "complete", "Regression pack finished clean."),
                ("EL-2403", "2026-04-12T09:58:00", "alert", "Latency exceeded target during long run."),
                ("EL-2404", "2026-04-12T09:40:00", "blocked", "Boot profile mismatch blocked validation."),
            ],
        )

        cursor.executemany(
            """
            INSERT INTO notes (run_id, author, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    "EL-2401",
                    "Steven",
                    "Need to compare recovery window changes against the last stable thermal pass.",
                    "2026-04-12T10:26:00",
                ),
                (
                    "EL-2403",
                    "Jordan",
                    "Looks like the bigger batch size is helping throughput but increasing jitter near the tail.",
                    "2026-04-12T10:00:00",
                ),
                (
                    "EL-2404",
                    "Anika",
                    "Rack should stay blocked until the validated boot profile is restored and artifact capture is rerun.",
                    "2026-04-12T09:42:00",
                ),
            ],
        )


def fetch_dashboard() -> dict:
    with connect() as connection:
        runs = connection.execute(
            "SELECT status, pass_rate, devices FROM runs ORDER BY updated_at DESC"
        ).fetchall()
        alerts = connection.execute(
            """
            SELECT id, run_id, severity, title, detail, created_at
            FROM alerts
            ORDER BY created_at DESC
            LIMIT 4
            """
        ).fetchall()

    active_runs = len(runs)
    devices_online = sum(row["devices"] for row in runs)
    alerts_open = len([row for row in alerts if row["severity"] in {"high", "medium"}])
    avg_pass_rate = round(sum(row["pass_rate"] for row in runs) / active_runs) if active_runs else 0

    return {
        "metrics": [
            {
                "label": "Active runs",
                "value": str(active_runs),
                "helper": "Live validation work in the queue",
                "tone": "neutral",
            },
            {
                "label": "Devices online",
                "value": str(devices_online),
                "helper": "Tracked systems across active benches",
                "tone": "positive",
            },
            {
                "label": "Open alerts",
                "value": str(alerts_open),
                "helper": "Items needing review or owner follow-up",
                "tone": "warning",
            },
            {
                "label": "Average pass rate",
                "value": f"{avg_pass_rate}%",
                "helper": "Current run health across the lab",
                "tone": "neutral",
            },
        ],
        "alerts": [dict(alert) for alert in alerts],
    }


def fetch_runs(search: str = "", status: str = "", environment: str = "", owner: str = "") -> list[dict]:
    clauses = []
    params: list[str] = []

    if search:
        clauses.append("(name LIKE ? OR platform LIKE ? OR summary LIKE ?)")
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])
    if status:
        clauses.append("status = ?")
        params.append(status)
    if environment:
        clauses.append("environment = ?")
        params.append(environment)
    if owner:
        clauses.append("owner = ?")
        params.append(owner)

    where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    query = f"""
        SELECT id, name, environment, platform, owner, status,
               started_at, updated_at, duration_minutes, pass_rate,
               anomalies, devices, summary
        FROM runs
        {where_clause}
        ORDER BY updated_at DESC, started_at DESC
    """

    with connect() as connection:
        rows = connection.execute(query, params).fetchall()

    return [dict(row) for row in rows]


def fetch_run_detail(run_id: str) -> dict | None:
    with connect() as connection:
        run = connection.execute(
            """
            SELECT id, name, environment, platform, owner, status,
                   started_at, updated_at, duration_minutes, pass_rate,
                   anomalies, devices, summary
            FROM runs
            WHERE id = ?
            """,
            (run_id,),
        ).fetchone()
        if run is None:
            return None

        alerts = connection.execute(
            """
            SELECT id, severity, title, detail, created_at
            FROM alerts
            WHERE run_id = ?
            ORDER BY created_at DESC
            """,
            (run_id,),
        ).fetchall()
        artifacts = connection.execute(
            """
            SELECT id, kind, name, size, status
            FROM artifacts
            WHERE run_id = ?
            ORDER BY id ASC
            """,
            (run_id,),
        ).fetchall()
        events = connection.execute(
            """
            SELECT id, timestamp, type, message
            FROM events
            WHERE run_id = ?
            ORDER BY timestamp DESC
            """,
            (run_id,),
        ).fetchall()
        diffs = connection.execute(
            """
            SELECT id, key, baseline, observed, impact
            FROM config_diffs
            WHERE run_id = ?
            ORDER BY id ASC
            """,
            (run_id,),
        ).fetchall()
        notes = connection.execute(
            """
            SELECT id, author, content, created_at
            FROM notes
            WHERE run_id = ?
            ORDER BY created_at DESC
            """,
            (run_id,),
        ).fetchall()

    return {
        **dict(run),
        "alerts": [dict(alert) for alert in alerts],
        "artifacts": [dict(artifact) for artifact in artifacts],
        "events": [dict(event) for event in events],
        "configDiffs": [dict(diff) for diff in diffs],
        "notes": [dict(note) for note in notes],
    }


def add_note(run_id: str, author: str, content: str, created_at: str) -> dict:
    with connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO notes (run_id, author, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (run_id, author, content, created_at),
        )
        note_id = cursor.lastrowid
        note = connection.execute(
            """
            SELECT id, author, content, created_at
            FROM notes
            WHERE id = ?
            """,
            (note_id,),
        ).fetchone()

    return dict(note)
