from __future__ import annotations

from cosmic_corridor.web import app


def test_health_endpoint_ok() -> None:
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
