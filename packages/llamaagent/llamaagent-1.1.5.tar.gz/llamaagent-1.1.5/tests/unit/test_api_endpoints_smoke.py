from fastapi.testclient import TestClient

from llamaagent.api import app


def test_root_and_health():
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    r = client.get("/health")
    assert r.status_code == 200
    r = client.get("/ready")
    assert r.status_code == 200
    r = client.get("/live")
    assert r.status_code == 200


def test_tools_and_agents_list():
    client = TestClient(app)
    r = client.get("/tools")
    assert r.status_code == 200
    data = r.json()
    assert "tools" in data
    r = client.get("/agents")
    assert r.status_code == 200


def test_agents_execute_mock():
    client = TestClient(app)
    payload = {"task": "Say hi", "agent_name": "ReactAgent", "context": {}}
    r = client.post("/agents/execute", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["success"] in (True, False)
    assert "result" in body

