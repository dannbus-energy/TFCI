from fastapi.testclient import TestClient
from api.main import app

c = TestClient(app)

def test_health():
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["jurisdictions"] == 208

def test_jurisdiction_detail():
    r = c.get("/v1/jurisdictions/greenland")
    assert r.status_code == 200
    assert r.json()["jurisdiction"]["iso2"] == "gl"
    assert len(r.json()["sector_scores"]) == 20

def test_filter_band():
    r = c.get("/v1/jurisdictions", params={"band": "HIGH"})
    assert all(j["credibilityBand"] == "HIGH" for j in r.json())
