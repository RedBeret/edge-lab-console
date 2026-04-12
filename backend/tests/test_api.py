from __future__ import annotations

import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


class EdgeLabApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)

    def test_health_endpoint(self) -> None:
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_dashboard_has_metrics_and_alerts(self) -> None:
        response = self.client.get("/api/dashboard")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload["metrics"]), 4)
        self.assertGreaterEqual(len(payload["alerts"]), 1)

    def test_runs_can_be_filtered(self) -> None:
        response = self.client.get("/api/runs", params={"status": "Blocked"})
        runs = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["id"], "EL-2404")

    def test_run_detail_returns_related_sections(self) -> None:
        response = self.client.get("/api/runs/EL-2401")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["id"], "EL-2401")
        self.assertGreaterEqual(len(payload["alerts"]), 1)
        self.assertGreaterEqual(len(payload["artifacts"]), 1)
        self.assertGreaterEqual(len(payload["configDiffs"]), 1)
        self.assertGreaterEqual(len(payload["notes"]), 1)

    def test_note_creation_persists(self) -> None:
        create_response = self.client.post(
            "/api/runs/EL-2402/notes",
            json={
                "author": "QA Lead",
                "content": "Verified the regression pack can be handed off as-is.",
            },
        )
        detail_response = self.client.get("/api/runs/EL-2402")

        self.assertEqual(create_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        self.assertTrue(
            any(
                note["content"] == "Verified the regression pack can be handed off as-is."
                for note in detail_response.json()["notes"]
            )
        )

    def test_unknown_run_returns_not_found(self) -> None:
        response = self.client.get("/api/runs/DOES-NOT-EXIST")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
