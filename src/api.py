"""HTTP surface for the customer models.

FastAPI reads the Pydantic models directly to build request validation and
the OpenAPI schema. The stored-customer schema is generated from the
SQLAlchemy model by pydantic-sqlalchemy, which only supports Pydantic v1.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from src.models import Customer, customer_to_dict
from src.records import CustomerRecord, StoredCustomer, stored_customer_from_record

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


@app.get("/records/example", response_model=StoredCustomer)
def example_record() -> dict:
    record = CustomerRecord(id=1, name="Ada Lovelace", email="ada@example.com", age=36)
    return stored_customer_from_record(record)
