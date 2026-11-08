import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "RAVEN" in data["app"]

def test_providers_status_endpoint():
    response = client.get("/api/providers/status")
    assert response.status_code == 200
    data = response.json()
    assert "gnani_prisma" in data
    assert "gnani_timbre" in data
    assert "evon_reasoning" in data
    assert data["gnani_prisma"]["model"] == "prisma-v3.0"

def test_demo_login():
    response = client.post("/api/auth/demo-login")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "analyst@raven.ai"

def test_list_investigations():
    response = client.get("/api/investigations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    sample = data[0]
    assert "Bengaluru" in sample["title"]

def test_sample_claims_and_evidence():
    # Fetch first investigation
    inv_resp = client.get("/api/investigations")
    inv_id = inv_resp.json()[0]["id"]

    # Fetch claims for this investigation
    claims_resp = client.get(f"/api/claims?investigation_id={inv_id}")
    assert claims_resp.status_code == 200
    claims = claims_resp.json()
    assert len(claims) >= 1

    first_claim = claims[0]
    assert "claim_text" in first_claim
    assert first_claim["status"] in ("refuted", "verified_supported", "unreviewed", "inconclusive")

    # Fetch evidence for this investigation
    ev_resp = client.get(f"/api/evidence?investigation_id={inv_id}")
    assert ev_resp.status_code == 200
    ev_list = ev_resp.json()
    assert len(ev_list) >= 1
    assert "title" in ev_list[0]

def test_report_generation():
    inv_resp = client.get("/api/investigations")
    inv_id = inv_resp.json()[0]["id"]

    report_payload = {
        "investigation_id": inv_id,
        "title": "Automated Verification Test Report",
        "executive_summary": "Smoke test summary of verified claims."
    }
    rep_resp = client.post("/api/reports/generate", json=report_payload)
    assert rep_resp.status_code == 200
    report_data = rep_resp.json()
    assert report_data["title"] == "Automated Verification Test Report"
    assert "verdict_summary" in report_data

def test_voice_briefing_synthesis():
    voice_payload = {
        "text": "This is a demonstration summary of the water potability investigation.",
        "voice": "Nalini",
        "language": "en-IN"
    }
    v_resp = client.post("/api/voice/briefing", json=voice_payload)
    assert v_resp.status_code == 200
    v_data = v_resp.json()
    assert "briefing_id" in v_data
    assert "audio_url" in v_data
