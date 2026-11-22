"""Tests for SQLite database operations."""

from __future__ import annotations

import sqlite3

from invoice_extractor.database import list_invoices, save_invoice
from invoice_extractor.models import ExtractionResult


def test_save_and_list_invoice(in_memory_db: sqlite3.Connection, sample_result: ExtractionResult):
    """Saving an invoice and listing it retrieves the correct fields and line items."""
    invoice_id = save_invoice(in_memory_db, sample_result, raw_input="Original text")
    assert invoice_id == 1

    invoices = list_invoices(in_memory_db)
    assert len(invoices) == 1

    saved = invoices[0]
    assert saved["id"] == 1
    assert saved["vendor_name"] == "Bright Pixel Studios Ltd."
    assert saved["invoice_date"] == "2024-03-15"
    assert saved["currency"] == "USD"
    assert saved["subtotal"] == 4599.00
    assert saved["tax_amount"] == 0.00
    assert saved["total_amount"] == 4599.00
    assert saved["raw_input"] == "Original text"
    assert saved["gemini_model"] == "gemini-3.5-flash-lite"
    assert saved["token_count"] == 150
    assert saved["response_time"] == 1.234

    # Check line items
    assert len(saved["line_items"]) == 4
    descriptions = [item["description"] for item in saved["line_items"]]
    amounts = [item["amount"] for item in saved["line_items"]]

    assert "Website redesign (Phase 1)" in descriptions
    assert 3200.00 in amounts
    assert 99.00 in amounts


def test_list_invoices_empty(in_memory_db: sqlite3.Connection):
    """Empty database returns an empty list."""
    invoices = list_invoices(in_memory_db)
    assert invoices == []
