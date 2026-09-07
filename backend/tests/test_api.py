import os
import sys
import io
import pytest
from fastapi.testclient import TestClient

# Ensure root workspace is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.main import app

client = TestClient(app)

def test_health_check():
    """Verify health check and root endpoints."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Gas Lift Allocation" in data["service"]

    response_health = client.get("/health")
    assert response_health.status_code == 200
    assert response_health.json()["status"] == "online"

def test_get_wells():
    """Verify wells retrieval endpoint (uses fallback mock if Snowflake is unavailable)."""
    response = client.get("/api/wells")
    assert response.status_code == 200
    wells = response.json()
    assert isinstance(wells, list)
    assert len(wells) > 0

def test_get_latest_tests():
    """Verify fetching latest production tests."""
    payload = {"well_names": ["Well 1", "Well 2"]}
    response = client.post("/api/wells/tests/latest", json=payload)
    assert response.status_code == 200
    tests = response.json()
    assert isinstance(tests, list)

def test_data_load_csv():
    """Verify CSV file upload and parsing via backend."""
    csv_content = (
        "description,,,,\n"
        "Field,Well 1,Well 2,,\n"
        "FieldA,Well 1,Well 2,,\n"
        "wct,0.15,0.20,,\n"
        "index,qgl 1,ql 1,qgl 2,ql 2\n"
        "1,50,100,60,120\n"
        "2,100,150,120,180\n"
        "3,200,200,240,240\n"
        "4,400,220,480,260\n"
        "5,600,230,700,270\n"
        "6,800,235,900,275\n"
    )
    file_tuple = ("test_data.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
    response = client.post("/api/data/load", files={"file": file_tuple})
    assert response.status_code == 200
    data = response.json()
    assert "q_gl_list" in data
    assert "q_fluid_list" in data
    assert "wct_list" in data
    assert "list_info" in data
    assert len(data["q_gl_list"]) == 2
    assert len(data["wct_list"]) == 2

def test_constrained_optimization():
    """Verify running constrained optimization pipeline."""
    payload = {
        "q_gl_list": [
            [50.0, 100.0, 200.0, 400.0, 600.0, 800.0],
            [60.0, 120.0, 240.0, 480.0, 700.0, 900.0]
        ],
        "q_fluid_list": [
            [100.0, 150.0, 200.0, 220.0, 230.0, 235.0],
            [120.0, 180.0, 240.0, 260.0, 270.0, 275.0]
        ],
        "wct_list": [0.15, 0.20],
        "list_info": ["TestField", "Well 1", "Well 2"],
        "qgl_limit": 1000.0,
        "qgl_min": 50.0,
        "p_qoil": 70.0,
        "p_qgl": 2.5
    }
    response = client.post("/api/optimization/constrained", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "optimization_results" in data
    assert "well_results" in data
    assert len(data["well_results"]) >= 2

def test_global_optimization():
    """Verify running global optimization pipeline."""
    payload = {
        "q_gl_list": [
            [50.0, 100.0, 200.0, 400.0, 600.0, 800.0],
            [60.0, 120.0, 240.0, 480.0, 700.0, 900.0]
        ],
        "q_fluid_list": [
            [100.0, 150.0, 200.0, 220.0, 230.0, 235.0],
            [120.0, 180.0, 240.0, 260.0, 270.0, 275.0]
        ],
        "wct_list": [0.15, 0.20],
        "list_info": ["TestField", "Well 1", "Well 2"],
        "qgl_min": 50.0,
        "p_qoil": 70.0,
        "p_qgl": 2.5,
        "max_iterations": 20,
        "max_qgl": 2000
    }
    response = client.post("/api/optimization/global", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_production" in data
    assert "total_qgl" in data
    assert "summary" in data

def test_optimization_history():
    """Verify retrieving optimization history."""
    response = client.get("/api/optimization/history?limit=5")
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    if len(history) > 0:
        opt_id = history[0]["id"]
        # Fetch specific details
        detail_res = client.get(f"/api/optimization/history/{opt_id}")
        assert detail_res.status_code == 200
        # Fetch well details
        wells_res = client.get(f"/api/optimization/history/{opt_id}/wells")
        assert wells_res.status_code == 200
