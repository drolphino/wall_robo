import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_add_wall_and_latest():
    wall_data = {
        "width": 10,
        "height": 10,
        "obstacles": [{"x":2,"y":2,"width":2,"height":2}]
    }
    response = client.post("/add_wall", json=wall_data)
    assert response.status_code == 200
    data = response.json()
    assert "wall_id" in data

    response2 = client.get("/latest_wall")
    assert response2.status_code == 200
    wall = response2.json()
    assert wall["width"] == 10
    assert wall["height"] == 10

def test_calculate_trajectory():
    wall = client.get("/latest_wall").json()
    wall_id = wall["wall_id"]
    response = client.get(f"/calculate_trajectory/{wall_id}")
    assert response.status_code == 200
    data = response.json()
    assert "total_cells_traversed" in data
    assert "section_paths" in data
