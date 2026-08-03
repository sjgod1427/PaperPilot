from starlette.testclient import TestClient

from paper_writing_pipeline.server import build_remote_app


def test_health_endpoint_requires_no_token():
    app = build_remote_app(auth_token="some-secret-token")
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_has_cors_header():
    app = build_remote_app(auth_token="some-secret-token")
    client = TestClient(app)

    response = client.get("/health", headers={"Origin": "https://example.com"})

    assert response.headers.get("access-control-allow-origin") == "*"


def test_other_routes_still_require_token():
    app = build_remote_app(auth_token="some-secret-token")
    client = TestClient(app)

    response = client.post("/mcp", json={})

    assert response.status_code == 401
