"""HTTP-level tests.

These are what make the Pydantic pin load-bearing rather than incidental:
FastAPI 0.99 derives request validation and the OpenAPI schema from the
same models, so the framework has to agree with them about which major
version of Pydantic is in play.
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
