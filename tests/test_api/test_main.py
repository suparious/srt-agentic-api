from fastapi.testclient import TestClient

def test_read_main(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SolidRusT Agentic API"}
