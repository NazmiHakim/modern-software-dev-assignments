from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models import Note

def test_pagination(client: TestClient):
    # Create 10 notes
    for i in range(10):
        client.post("/notes/", json={"title": f"Note {i:02d}", "content": "Content"})
    
    # Test limit
    r = client.get("/notes/", params={"limit": 5, "sort": "title"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 5
    assert data[0]["title"] == "Note 00"
    
    # Test offset (skip first 5 notes: 0,1,2,3,4 -> next is 5)
    r = client.get("/notes/", params={"skip": 5, "limit": 5, "sort": "title"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 5
    assert data[0]["title"] == "Note 05"

def test_sorting(client: TestClient):
    # Notes are already created from previous test (if using same DB, but conftest creates fresh)
    # So let's create a few specific ones
    client.post("/notes/", json={"title": "AAA", "content": "Content"})
    client.post("/notes/", json={"title": "ZZZ", "content": "Content"})
    
    # Sort by title asc
    r = client.get("/notes/", params={"sort": "title"})
    assert r.status_code == 200
    data = r.json()
    titles = [n["title"] for n in data]
    assert titles == sorted(titles)
    assert titles[0] == "AAA"
    
    # Sort by title desc
    r = client.get("/notes/", params={"sort": "-title"})
    assert r.status_code == 200
    data = r.json()
    titles = [n["title"] for n in data]
    assert titles == sorted(titles, reverse=True)
    assert titles[0] == "ZZZ"
