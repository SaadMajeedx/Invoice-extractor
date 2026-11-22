"""Tests for Pydantic models, validation, and math reconciliation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from invoice_extractor.models import Invoice, LineItem


def test_valid_invoice(sample_invoice: Invoice):
    """A correctly formed invoice parses and validates."""
    assert sample_invoice.vendor_name == "Bright Pixel Studios Ltd."
    assert sample_invoice.subtotal == 4599.00
    assert sample_invoice.tax_amount == 0.00
    assert sample_invoice.total_amount == 4599.00
    assert sample_invoice.currency == "USD"
    assert len(sample_invoice.line_items) == 4


def test_valid_italian_invoice_with_tax(sample_italian_invoice: Invoice):
    """An invoice with VAT/tax reconciles properly."""
    assert sample_italian_invoice.vendor_name == "Rossi & Bianchi S.r.l."
    assert sample_italian_invoice.subtotal == 4195.00
    assert sample_italian_invoice.tax_amount == 922.90
    assert sample_italian_invoice.total_amount == 5117.90


def test_reconciliation_fails_when_line_items_dont_match_subtotal():
    """Fail loudly if sum of line_items does not match subtotal."""
    with pytest.raises(ValidationError) as exc_info:
        Invoice(
            vendor_name="Acme Corp",
            invoice_date="2024-01-01",
            currency="USD",
            subtotal=150.00,  # Line items only sum to 100.00
            tax_amount=0.00,
            total_amount=150.00,
            line_items=[
                LineItem(description="Item A", amount=60.00),
                LineItem(description="Item B", amount=40.00),
            ],
        )
    assert "Reconciliation error: sum of line items (100.00) does not match subtotal (150.00)" in str(exc_info.value)


def test_reconciliation_fails_when_subtotal_plus_tax_dont_match_total():
    """Fail loudly if subtotal + tax_amount does not match total_amount."""
    with pytest.raises(ValidationError) as exc_info:
        Invoice(
            vendor_name="Acme Corp",
            invoice_date="2024-01-01",
            currency="EUR",
            subtotal=100.00,
            tax_amount=22.00,
            total_amount=150.00,  # Should be 122.00
            line_items=[
                LineItem(description="Service", amount=100.00),
            ],
        )
    assert "Reconciliation error: subtotal (100.00) + tax_amount (22.00) = 122.00" in str(exc_info.value)


def test_reconciliation_rounding_tolerance():
    """Math differences <= 0.02 (e.g. fractional cent rounding) are accepted."""
    inv = Invoice(
        vendor_name="Tolerance Test",
        invoice_date="2024-01-01",
        currency="USD",
        subtotal=10.00,
        tax_amount=1.51,
        total_amount=11.52,  # 10.00 + 1.51 = 11.51, difference of 0.01 is within 0.02 tolerance
        line_items=[
            LineItem(description="Item 1", amount=10.01),  # difference of 0.01 with subtotal
        ],
    )
    assert inv.total_amount == 11.52


def test_missing_total_amount_fails_loudly():
    """An invoice missing total_amount raises a ValidationError (fail loudly)."""
    with pytest.raises(ValidationError) as exc_info:
        Invoice(
            vendor_name="Acme Corp",
            invoice_date="2024-01-01",
            currency="USD",
            line_items=[LineItem(description="Item 1", amount=100.0)],
        )
    assert "total_amount" in str(exc_info.value)


def test_zero_or_negative_total_amount_fails():
    """total_amount must be strictly positive (> 0)."""
    with pytest.raises(ValidationError):
        Invoice(
            vendor_name="Acme Corp",
            invoice_date="2024-01-01",
            currency="USD",
            total_amount=0.0,
            line_items=[LineItem(description="Item 1", amount=0.0)],
        )


def test_currency_normalized_to_uppercase():
    """Currency should be automatically uppercased."""
    inv = Invoice(
        vendor_name="Test Vendor",
        invoice_date="2024-01-01",
        currency="eur",
        subtotal=100.0,
        tax_amount=0.0,
        total_amount=100.0,
        line_items=[LineItem(description="Consulting", amount=100.0)],
    )
    assert inv.currency == "EUR"


def test_empty_line_items_fails():
    """An invoice must contain at least one line item."""
    with pytest.raises(ValidationError):
        Invoice(
            vendor_name="Test Vendor",
            invoice_date="2024-01-01",
            currency="EUR",
            total_amount=100.0,
            line_items=[],
        )
