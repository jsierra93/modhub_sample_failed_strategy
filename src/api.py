"""HTTP surface for the customer models.

FastAPI 0.99 reads the Pydantic models directly to build request
validation and the OpenAPI schema, so the framework and the models are
pinned to the same major version of Pydantic.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from src.models import Customer, customer_to_dict

app = FastAPI(title="Customer API", version="0.1.0")

_CUSTOMERS: dict[str, Customer] = {}


@app.post("/customers", status_code=201)
def create_customer(customer: Customer) -> dict:
    _CUSTOMERS[customer.email] = customer
    return customer_to_dict(customer)


@app.get("/customers/{email}")
def get_customer(email: str) -> dict:
    customer = _CUSTOMERS.get(email)
    if customer is None:
        raise HTTPException(status_code=404, detail="customer not found")
    return customer_to_dict(customer)


@app.post("/customers/validate")
def validate_customer(payload: dict) -> dict:
    try:
        Customer.parse_obj(payload)
    except ValidationError as exc:
        return {"valid": False, "error_count": len(exc.errors())}
    return {"valid": True, "error_count": 0}
