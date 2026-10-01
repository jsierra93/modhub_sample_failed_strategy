"""HTTP-level tests.

FastAPI derives request validation and the OpenAPI schema from the same
models, and the stored-customer schema comes from pydantic-sqlalchemy.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)

VALID_PAYLOAD = {
    "name": "Ada Lovelace",
    "email": "ada@example.com",
    "age": 36,
    "addresses": [{"street": "1 Analytical Way", "city": "London", "postal_code": "12345"}],
}


def test_creating_a_customer_returns_201():
    response = client.post("/customers", json=VALID_PAYLOAD)

    assert response.status_code == 201
    assert response.json()["email"] == "ada@example.com"


def test_created_customer_can_be_read_back():
    client.post("/customers", json=VALID_PAYLOAD)

    response = client.get("/customers/ada@example.com")

    assert response.status_code == 200
    assert response.json()["name"] == "Ada Lovelace"


def test_unknown_customer_returns_404():
    response = client.get("/customers/nobody@example.com")

    assert response.status_code == 404


def test_framework_rejects_an_invalid_body():
    response = client.post("/customers", json={**VALID_PAYLOAD, "age": 17})

    assert response.status_code == 422


def test_validate_endpoint_reports_a_valid_payload():
    response = client.post("/customers/validate", json=VALID_PAYLOAD)

    assert response.json() == {"valid": True, "error_count": 0}


def test_validate_endpoint_counts_errors():
    response = client.post("/customers/validate", json={**VALID_PAYLOAD, "email": "nope"})

    body = response.json()
    assert body["valid"] is False
    assert body["error_count"] >= 1


def test_openapi_schema_is_generated_from_the_models():
    schema = client.get("/openapi.json").json()

    assert "Customer" in schema["components"]["schemas"]


def test_stored_customer_schema_is_generated_from_the_orm_model():
    schema = client.get("/openapi.json").json()

    assert "CustomerRecord" in schema["components"]["schemas"]


def test_example_record_is_served_through_the_generated_schema():
    response = client.get("/records/example")

    assert response.status_code == 200
    assert response.json()["email"] == "ada@example.com"
