"""Persistence-side view of a customer.

The API schema for stored customers is not written by hand: it is generated
from the SQLAlchemy model by `pydantic-sqlalchemy`, so the two can never drift.
"""

from __future__ import annotations

from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CustomerRecord(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    age = Column(Integer, nullable=False)


StoredCustomer = sqlalchemy_to_pydantic(CustomerRecord)


def stored_customer_from_record(record: CustomerRecord) -> dict:
    return StoredCustomer.from_orm(record).dict()
