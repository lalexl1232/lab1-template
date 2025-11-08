import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_person():
    response = client.post(
        "/api/v1/persons",
        json={"name": "John Doe", "age": 30, "address": "123 Main St", "work": "Engineer"}
    )
    assert response.status_code == 201
    assert "Location" in response.headers
    assert "/api/v1/persons/" in response.headers["Location"]


def test_get_all_persons():
    client.post("/api/v1/persons", json={"name": "John Doe", "age": 30})
    client.post("/api/v1/persons", json={"name": "Jane Doe", "age": 25})

    response = client.get("/api/v1/persons")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "John Doe"
    assert data[1]["name"] == "Jane Doe"


def test_get_person_by_id():
    create_response = client.post("/api/v1/persons", json={"name": "John Doe", "age": 30})
    location = create_response.headers["Location"]
    person_id = location.split("/")[-1]

    response = client.get(f"/api/v1/persons/{person_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["age"] == 30


def test_get_person_not_found():
    response = client.get("/api/v1/persons/999")
    assert response.status_code == 404


def test_update_person():
    create_response = client.post("/api/v1/persons", json={"name": "John Doe", "age": 30})
    location = create_response.headers["Location"]
    person_id = location.split("/")[-1]

    response = client.patch(
        f"/api/v1/persons/{person_id}",
        json={"name": "John Updated", "age": 31}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Updated"
    assert data["age"] == 31


def test_delete_person():
    create_response = client.post("/api/v1/persons", json={"name": "John Doe", "age": 30})
    location = create_response.headers["Location"]
    person_id = location.split("/")[-1]

    response = client.delete(f"/api/v1/persons/{person_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/persons/{person_id}")
    assert get_response.status_code == 404
