"""Shared pytest fixtures for invoice-extractor tests."""

from __future__ import annotations

import sqlite3

import pytest

from invoice_extractor.database import init_db
from invoice_extractor.models import ExtractionResult, Invoice, LineItem


@pytest.fixture
def sample_invoice() -> Invoice:
    """A valid Invoice built from the English sample data."""
    return Invoice(
        vendor_name="Bright Pixel Studios Ltd.",
        invoice_date="2024-03-15",
        currency="USD",
        subtotal=4599.00,
        tax_amount=0.00,
        total_amount=4599.00,
        line_items=[
            LineItem(description="Website redesign (Phase 1)", amount=3200.00),
            LineItem(description="SEO audit & optimization", amount=850.00),
            LineItem(description="Monthly hosting (3 months)", amount=450.00),
            LineItem(description="SSL certificate (annual renewal)", amount=99.00),
        ],
    )


@pytest.fixture
def sample_italian_invoice() -> Invoice:
    """A valid Italian Invoice with 22% IVA tax."""
    return Invoice(
        vendor_name="Rossi & Bianchi S.r.l.",
        invoice_date="2024-02-22",
        currency="EUR",
        subtotal=4195.00,
        tax_amount=922.90,
        total_amount=5117.90,
        line_items=[
            LineItem(description="Consulenza strategica (8 ore)", amount=1200.00),
            LineItem(description="Sviluppo sito web aziendale", amount=2800.00),
            LineItem(description="Hosting annuale (server dedicato)", amount=180.00),
            LineItem(description="Rinnovo dominio (.it)", amount=15.00),
        ],
    )


@pytest.fixture
def sample_result(sample_invoice: Invoice) -> ExtractionResult:
    """An ExtractionResult wrapping the sample invoice."""
    return ExtractionResult(
        invoice=sample_invoice,
        token_count=150,
        response_time_s=1.234,
        model_used="gemini-3.5-flash-lite",
    )


@pytest.fixture
def in_memory_db():
    """Yield an in-memory SQLite connection with tables already created."""
    conn = init_db(":memory:")
    yield conn
    conn.close()
