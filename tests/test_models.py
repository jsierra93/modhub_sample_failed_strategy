"""Behaviour tests.

Deliberately written against the helper functions in src.models rather
than Pydantic's own API, and never asserting on validation *messages*
(their wording is version-specific). What each test pins down is what the
project promises its callers, so the suite stays meaningful across a
Pydantic upgrade.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from src.models import (
    build_customer,
    customer_field_names,
    customer_to_dict,
    customer_to_json,
)

VALID_PAYLOAD = {
    "name": "Ada Lovelace",
    "email": "ada@example.com",
    "age": 36,
    "addresses": [{"street": "1 Analytical Way", "city": "London", "postal_code": "12345"}],
}


def test_builds_a_customer_from_a_valid_payload():
    customer = build_customer(VALID_PAYLOAD)

    assert customer.name == "Ada Lovelace"
    assert customer.email == "ada@example.com"
    assert customer.age == 36


def test_nested_addresses_are_parsed_into_models():
    customer = build_customer(VALID_PAYLOAD)

    assert len(customer.addresses) == 1
    assert customer.addresses[0].city == "London"


def test_optional_nickname_defaults_to_none():
    customer = build_customer(VALID_PAYLOAD)

    assert customer.nickname is None


def test_addresses_default_to_an_empty_list():
    payload = {key: value for key, value in VALID_PAYLOAD.items() if key != "addresses"}

    customer = build_customer(payload)

    assert customer.addresses == []


def test_serialising_to_dict_round_trips():
    customer = build_customer(VALID_PAYLOAD)

    as_dict = customer_to_dict(customer)

    assert as_dict["name"] == "Ada Lovelace"
    assert as_dict["addresses"][0]["postal_code"] == "12345"


def test_serialising_to_json_produces_valid_json():
    customer = build_customer(VALID_PAYLOAD)

    parsed = json.loads(customer_to_json(customer))

    assert parsed["email"] == "ada@example.com"
    assert parsed["age"] == 36


def test_age_below_eighteen_is_rejected():
    payload = {**VALID_PAYLOAD, "age": 17}

    with pytest.raises(ValidationError):
        build_customer(payload)


def test_email_without_an_at_sign_is_rejected():
    payload = {**VALID_PAYLOAD, "email": "not-an-email"}

    with pytest.raises(ValidationError):
        build_customer(payload)


def test_blank_name_is_rejected():
    payload = {**VALID_PAYLOAD, "name": "   "}

    with pytest.raises(ValidationError):
        build_customer(payload)


def test_non_numeric_postal_code_is_rejected():
    payload = {
        **VALID_PAYLOAD,
        "addresses": [{"street": "1 Analytical Way", "city": "London", "postal_code": "ABCDE"}],
    }

    with pytest.raises(ValidationError):
        build_customer(payload)


def test_too_short_postal_code_is_rejected():
    payload = {
        **VALID_PAYLOAD,
        "addresses": [{"street": "1 Analytical Way", "city": "London", "postal_code": "12"}],
    }

    with pytest.raises(ValidationError):
        build_customer(payload)


def test_field_names_are_exposed_in_declaration_order():
    assert customer_field_names() == ["name", "email", "age", "addresses", "nickname"]
